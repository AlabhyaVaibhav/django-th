from django.contrib import admin

#from .models import ServicesActivated
from .forms.services import ServicesAdminForm
from .models.services import ServicesMgr
#from .models.rss import ServiceRss
#from .models.evernote import ServiceEvernote


class ServicesManagedAdmin(admin.ModelAdmin):
    """
        get the list of the available services (the activated one)
    """
    list_display = ('name', 'status', 'description')

    add_form = ServicesAdminForm
    view_form = ServicesAdminForm

    def get_form(self, request, obj=None, **args):
        defaults = {}
        if obj is None:
            defaults.update({'form': self.add_form, })
        else:
            defaults.update({'form': self.view_form, })
        defaults.update(args)
        return super(ServicesManagedAdmin, self).get_form(request, obj,
                                                          **defaults)

admin.site.register(ServicesMgr, ServicesManagedAdmin)
