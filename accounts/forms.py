from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=False, label="Phone Number")

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200"
            )

        self.fields["username"].widget.attrs["placeholder"] = "Choose a username"
        self.fields["email"].widget.attrs["placeholder"] = "Enter your email"
        self.fields["first_name"].widget.attrs["placeholder"] = "First name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Last name"
        self.fields["phone"].widget.attrs["placeholder"] = "Phone number (optional)"
        self.fields["password1"].widget.attrs["placeholder"] = "Create a password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm your password"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone_number = self.cleaned_data.get("phone")
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone_number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200"
            )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            # Check if username already exists for other users (excluding current user)
            if (
                User.objects.filter(username=username)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise forms.ValidationError(
                    "Username already exists. Please choose a different username."
                )
        return username


class CustomPasswordChangeForm(forms.Form):
    """Custom password change form without requiring old password"""

    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(),
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200"
            )

        self.fields["new_password1"].widget.attrs["placeholder"] = "Enter new password"
        self.fields["new_password2"].widget.attrs[
            "placeholder"
        ] = "Confirm new password"

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class AdminUserCreateForm(forms.ModelForm):
    """Form for admin to create new users with role selection"""

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(),
        help_text="Enter a strong password for the user.",
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(),
        help_text="Enter the same password as before, for verification.",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        # Extract current user if provided
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)

        # Set role choices based on current user permissions
        if self.current_user:
            if self.current_user.is_admin:
                # Admin can create any role
                self.fields["role"].choices = User.ROLE_CHOICES
            elif self.current_user.is_staff_member:
                # Staff can only create customer accounts
                self.fields["role"].choices = [("customer", "Customer")]
                self.fields["role"].initial = "customer"
                self.fields["role"].widget.attrs["readonly"] = True
            else:
                # Non-admin/staff should not access this form, but just in case
                self.fields["role"].choices = [("customer", "Customer")]
                self.fields["role"].initial = "customer"

        for field_name, field in self.fields.items():
            if field_name == "is_active":
                field.widget.attrs["class"] = (
                    "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                )
            else:
                field.widget.attrs["class"] = (
                    "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                )

        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["email"].widget.attrs["placeholder"] = "Email address"
        self.fields["first_name"].widget.attrs["placeholder"] = "First name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Last name"
        self.fields["phone_number"].widget.attrs[
            "placeholder"
        ] = "Phone number (optional)"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm password"

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AdminUserEditForm(forms.ModelForm):
    """Form for admin to edit existing users"""

    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label="New password",
        help_text="Leave blank to keep the current password unchanged.",
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label="Confirm new password",
        help_text="Re-enter the new password for confirmation.",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "is_active",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == "is_active":
                field.widget.attrs["class"] = (
                    "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                )
            else:
                field.widget.attrs["class"] = (
                    "w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                )

        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["email"].widget.attrs["placeholder"] = "Email address"
        self.fields["first_name"].widget.attrs["placeholder"] = "First name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Last name"
        self.fields["phone_number"].widget.attrs[
            "placeholder"
        ] = "Phone number (optional)"
        self.fields["new_password"].widget.attrs[
            "placeholder"
        ] = "Enter new password (optional)"
        self.fields["confirm_password"].widget.attrs[
            "placeholder"
        ] = "Confirm new password"

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # If a new password is provided, confirm password must match
        if new_password or confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError(
                    "New password and confirmation password do not match."
                )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Only change password if a new one was provided
        if self.cleaned_data.get("new_password"):
            user.set_password(self.cleaned_data["new_password"])
        if commit:
            user.save()
        return user
