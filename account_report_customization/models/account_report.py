import io
import markupsafe
from datetime import datetime

from odoo import models, fields, api
from itertools import groupby

class AccountReport(models.Model):
    _inherit = 'account.report'

    def _get_pdf_export_html(self, options, lines, additional_context=None, template=None):
        report_info = self.get_report_information(options)

        custom_print_templates = report_info['custom_display'].get('pdf_export', {})
        template = custom_print_templates.get('pdf_export_main', 'account_report_customization.pdf_export_isy')
        render_values = {
            'report': self,
            'report_title': self.name,
            'options': options,
            'table_start': markupsafe.Markup('<tbody>'),
            'table_end': markupsafe.Markup('''
                </tbody></table>
                <div style="page-break-after: always"></div>
                <table class="o_table table-hover">
            '''),
            'column_headers_render_data': self._get_column_headers_render_data(options),
            'custom_templates': custom_print_templates,
            'printed_on': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'company_name': report_info['report']['company_name'],
            'currency_symbol': report_info['report']['company_currency_symbol']
        }
        if additional_context:
            render_values.update(additional_context)

        if options.get('order_column'):
            lines = self.sort_lines(lines, options)

        lines = self._format_lines_for_display(lines, options)

        render_values['lines'] = lines

        # Manage footnotes.
        footnotes_to_render = []
        number = 0
        for line in lines:
            footnote_data = report_info['footnotes'].get(str(line.get('id')))
            if footnote_data:
                number += 1
                line['footnote'] = str(number)
                footnotes_to_render.append({'id': footnote_data['id'], 'number': number, 'text': footnote_data['text']})

        render_values['footnotes'] = footnotes_to_render

        options['css_custom_class'] = report_info['custom_display'].get('css_custom_class', '')

        # Render.
        return self.env['ir.qweb']._render(template, render_values)

    def export_to_pdf(self, options):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.company,
        }

        print_options = self.get_options(previous_options={**options, 'export_mode': 'print'})
        if print_options['sections']:
            reports_to_print = self.env['account.report'].browse([section['id'] for section in print_options['sections']])
        else:
            reports_to_print = self

        reports_options = []
        for report in reports_to_print:
            reports_options.append(report.get_options(previous_options={**print_options, 'selected_section_id': report.id}))

        grouped_reports_by_format = groupby(
            zip(reports_to_print, reports_options),
            key=lambda report: len(report[1]['columns']) > 5
        )

        footer = self.env['ir.actions.report']._render_template("account_reports.internal_layout", values=rcontext)
        footer = self.env['ir.actions.report']._render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=markupsafe.Markup(footer.decode())))

        action_report = self.env['ir.actions.report']
        files_stream = []
        for is_landscape, reports_with_options in grouped_reports_by_format:
            bodies = []

            for report, report_options in reports_with_options:
                bodies.append(report._get_pdf_export_html(
                    report_options,
                    report._filter_out_folded_children(report._get_lines(report_options)),
                    additional_context={'base_url': base_url}
                ))

            files_stream.append(
                io.BytesIO(action_report._run_wkhtmltopdf(
                    bodies,
                    footer=footer.decode(),
                    landscape=is_landscape or self._context.get('force_landscape_printing'),
                    specific_paperformat_args={
                        'data-report-margin-top': 10,
                        'data-report-header-spacing': 10,
                        'data-report-margin-bottom': 15,
                    }
                )
            ))

        if len(files_stream) > 1:
            result_stream = action_report._merge_pdfs(files_stream)
            result = result_stream.getvalue()
            # Close the different stream
            result_stream.close()
            for file_stream in files_stream:
                file_stream.close()
        else:
            result = files_stream[0].read()

        return {
            'file_name': self.get_default_report_filename(options, 'pdf'),
            'file_content': result,
            'file_type': 'pdf',
        }
