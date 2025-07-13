from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from .models import *

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email address'),
            'autocomplete': 'email'
        }),
        error_messages={
            'required': _('Email is required'),
            'invalid': _('Enter a valid email address')
        }
    )

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Username'),
                'autocomplete': 'username'
            }),
        }
        error_messages = {
            'username': {
                'unique': _('This username is already taken'),
                'required': _('Username is required')
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Password'),
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm Password'),
            'autocomplete': 'new-password'
        })

class RetailerRegistrationForm(forms.ModelForm):
    terms = forms.BooleanField(
        label=_("I agree to the terms and conditions"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={
            'required': _('You must accept the terms and conditions')
        }
    )

    class Meta:
        model = Retailer
        fields = ['company_name', 'address', 'contact_number']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Company Name')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Full business address')
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Contact phone number')
            }),
        }
        labels = {
            'company_name': _('Company Name'),
            'address': _('Business Address'),
            'contact_number': _('Contact Number')
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username or Email"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Username or email'),
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Password'),
            'autocomplete': 'current-password'
        })
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct username/email and password."
        ),
        'inactive': _("This account is inactive."),
    }

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your account email'),
            'autocomplete': 'email'
        })
    )

class ProductForm(forms.ModelForm):
    current_stock = forms.IntegerField(
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0'
        })
    )
    min_stock_level = forms.IntegerField(
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0'
        })
    )
    lead_time_days = forms.IntegerField(
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1'
        })
    )

    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'description', 
            'price', 'current_stock', 'min_stock_level',
            'lead_time_days', 'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Product name')
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('SKU code')
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Product description')
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'sku': _('SKU Code'),
            'lead_time_days': _('Lead Time (days)')
        }

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        if Product.objects.filter(sku=sku).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_('This SKU already exists'))
        return sku

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'latitude', 'longitude', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Warehouse name')
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Physical address')
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': _('e.g. 40.7128')
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': _('e.g. -74.0060')
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': _('Total capacity in units')
            })
        }
        help_texts = {
            'latitude': _('Decimal degrees format'),
            'longitude': _('Decimal degrees format')
        }

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        if (latitude is not None and longitude is None) or \
           (longitude is not None and latitude is None):
            raise forms.ValidationError(
                _('Both latitude and longitude must be provided together')
            )
        return cleaned_data

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Full name')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Email address')
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Phone number')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Shipping address')
            })
        }

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }

class DeliveryRouteForm(forms.ModelForm):
    start_time = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={'type': 'date', 'class': 'form-control'},
            time_attrs={'type': 'time', 'class': 'form-control'}
        )
    )

    class Meta:
        model = DeliveryRoute
        fields = ['driver_name', 'driver_contact', 'vehicle_type', 'start_time']
        widgets = {
            'driver_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Driver's full name")
            }),
            'driver_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Driver's phone number")
            }),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'})
        }

class InventoryUpdateForm(forms.ModelForm):
    adjustment = forms.IntegerField(
        label=_("Adjustment Quantity"),
        help_text=_("Positive for addition, negative for subtraction"),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter adjustment amount')
        })
    )
    reason = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Reason for adjustment (optional)')
        })
    )

    class Meta:
        model = Inventory
        fields = []

    def save(self, commit=True):
        adjustment = self.cleaned_data.get('adjustment', 0)
        self.instance.quantity += adjustment
        return super().save(commit)

class DemandForecastForm(forms.ModelForm):
    class Meta:
        model = DemandForecast
        fields = ['forecast_period']
        widgets = {
            'forecast_period': forms.Select(attrs={'class': 'form-select'})
        }