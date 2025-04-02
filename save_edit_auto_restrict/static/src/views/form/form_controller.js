/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

const originalSetup = FormController.prototype.setup;

patch(FormController.prototype, {
    setup() {
        this.props.preventEdit = this.env.inDialog ? false : true;
        originalSetup.call(this);
    },

    async beforeLeave() {
        if (this.model.root.isDirty && this.beforeLeaveHook === false) {
            if (confirm("Do you want to save changes before leaving?")) {
                this.beforeLeaveHook = true;
                await this.model.root.save({
                    reload: false,
                    onError: this.onSaveError.bind(this),
                });
            } else {
                this.beforeLeaveHook = true;
                this.model.root.discard();
            }
        }
    },

    beforeUnload: async (ev) => {
        if (this.model.root.isDirty) {
            ev.preventDefault();
            ev.returnValue = '';
        }
    },

    // Prevent auto-save on navigation
    async _onWillNavigate() {
        if (this.model.root.isDirty) {
            if (confirm("Do you want to save changes before leaving?")) {
                await this.model.root.save({
                    reload: false,
                    onError: this.onSaveError.bind(this),
                });
            } else {
                this.model.root.discard();
            }
        }
    },

    // Override the default save behavior
    async save() {
        if (this.model.root.isDirty) {
            await this.model.root.save({
                reload: false,
                onError: this.onSaveError.bind(this),
            });
        }
    }
}); 