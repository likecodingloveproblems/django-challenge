from django import forms
from django.utils.translation import gettext_lazy as _


class MatchAdminAddForm(forms.ModelForm):
    """
    Form used in match admin panel to create matches
    """

    does_create_seats = forms.BooleanField(
        label=_("Does create seats?"),
        required=True,
        initial=True,
        help_text=_("Base on the stadium capacity all the seats will be created."),
    )

    class Meta:
        fields = ["host_team", "guest_team", "stadium", "datetime"]
