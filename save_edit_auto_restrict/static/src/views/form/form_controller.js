/** @odoo-module */
import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useSetupView } from "@web/views/view_hook";
import { browser } from "@web/core/browser/browser";

const originalSetup = FormController.prototype.setup;

patch(FormController.prototype, {
/* Patch FormController to restrict auto save in form views */
   setup(){
      super.setup(...arguments);
      this.beforeLeaveHook = false;
      useSetupView({
          beforeLeave: () => this.beforeLeave(),
          beforeUnload: (ev) => this.beforeUnload(ev),
      });
   },
   async beforeLeave() {
   /* function will work before leave the form */
      if(this.model.root.isDirty && this.beforeLeaveHook === false && this.model.root.mode === 'edit'){
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
       if (this.model.root.isDirty && this.model.root.mode === 'edit') {
           ev.preventDefault();
           ev.returnValue = '';
       }
   },
   async save() {
       if (this.model.root.isDirty) {
           await this.model.root.save({
               reload: false,
               onError: this.onSaveError.bind(this),
           });
       }
   },
   async _onWillNavigate() {
       if (this.model.root.isDirty && this.model.root.mode === 'edit') {
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
   async discard() {
       if (this.model.root.isDirty) {
           this.model.root.discard();
       }
   },
   async _onChange() {
       // Do nothing to prevent auto-save
       return;
   },
   async _onPopState() {
       if (this.model.root.isDirty && this.model.root.mode === 'edit') {
           if (confirm("Do you want to save changes before leaving?")) {
               await this.model.root.save({
                   reload: false,
                   onError: this.onSaveError.bind(this),
               });
           } else {
               this.model.root.discard();
           }
       }
   }
});
