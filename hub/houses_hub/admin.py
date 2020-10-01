from django.contrib import admin
from django import forms
from login_register_service_hub.models import CustomUser
from .models import Lease, House, Application, ApplicationInfo


# Register your models here.


class LeaseForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = '__all__'

    students = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(usertype=CustomUser.USERTYPE_DICT["STUDENT"]), required=False)

    def __init__(self, *args, **kwargs):
        super(LeaseForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['students'].initial = self.instance.students.all()
        else:
            self.fields['students'].initial = []

    def save(self, *args, **kwargs):
        # Fix this later
        instance = super(LeaseForm, self).save(commit = False)
        if not instance.pk:
            instance.save()
        instance.students.clear()
        it = self.cleaned_data['students'].iterator()
        while (True):
            try:
                instance.students.add(next(it))
            except StopIteration:
                break

        return instance


class LeaseAdmin(admin.ModelAdmin):
    form = LeaseForm


admin.site.register(Lease, LeaseAdmin)
admin.site.register(House)
admin.site.register(Application)
admin.site.register(ApplicationInfo)