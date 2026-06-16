from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from orders.models import Address, Payment
from accounts.models import UserProfile
from catalog.models import Review


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-input")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            UserProfile.objects.create(user=user, phone=self.cleaned_data.get("phone", ""))
        return user


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ("full_name", "line1", "city", "state", "pincode")
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full name"}),
            "line1": forms.TextInput(attrs={"placeholder": "Street address"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "state": forms.TextInput(attrs={"placeholder": "State"}),
            "pincode": forms.TextInput(attrs={"placeholder": "Pincode"}),
        }


class CheckoutForm(forms.Form):
    use_saved = forms.BooleanField(required=False, initial=False)
    saved_address = forms.ModelChoiceField(
        queryset=Address.objects.none(), required=False, empty_label=None
    )
    payment_method = forms.ChoiceField(
        choices=[
            (Payment.Method.RAZORPAY, "Razorpay (UPI / Card / Netbanking)"),
            (Payment.Method.COD, "Cash on Delivery"),
        ],
        initial=Payment.Method.RAZORPAY,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        addresses = Address.objects.filter(user=user)
        self.fields["saved_address"].queryset = addresses
        if addresses.exists():
            self.fields["use_saved"].initial = True
            self.fields["saved_address"].initial = addresses.filter(is_default=True).first() or addresses.first()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("use_saved") and not cleaned.get("saved_address"):
            raise forms.ValidationError("Please select a saved address.")
        return cleaned


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "title", "comment")
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} star{'s' if i > 1 else ''}") for i in range(5, 0, -1)]
            ),
            "title": forms.TextInput(attrs={"placeholder": "Summarize your experience"}),
            "comment": forms.Textarea(attrs={"placeholder": "What did you like or dislike?", "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-input")


class ProfileForm(forms.ModelForm):
    phone = forms.CharField(max_length=15, required=False, label="Phone")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = getattr(self.instance, "profile", None)
        if profile:
            self.fields["phone"].initial = profile.phone
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-input")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get("phone", "")
            profile.save(update_fields=["phone"])
        return user

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if email and User.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class ProfileAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ("full_name", "line1", "city", "state", "pincode", "is_default")
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full name", "class": "form-input"}),
            "line1": forms.TextInput(attrs={"placeholder": "Street address", "class": "form-input"}),
            "city": forms.TextInput(attrs={"placeholder": "City", "class": "form-input"}),
            "state": forms.TextInput(attrs={"placeholder": "State", "class": "form-input"}),
            "pincode": forms.TextInput(attrs={"placeholder": "Pincode", "class": "form-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_default"].widget.attrs.setdefault("class", "")
