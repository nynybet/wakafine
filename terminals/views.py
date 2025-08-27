from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Terminal
from .forms import TerminalForm


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only admin users can access admin views"""

    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_admin or self.request.user.is_staff_member
        )


# Public Views
class TerminalListView(ListView):
    model = Terminal
    template_name = "terminals/terminal_list.html"
    context_object_name = "terminals"
    paginate_by = 20

    def get_queryset(self):
        queryset = Terminal.objects.filter(is_active=True).order_by("name")
        search = self.request.GET.get("search")
        terminal_type = self.request.GET.get("type")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(location__icontains=search)
                | Q(city__icontains=search)
            )

        if terminal_type:
            queryset = queryset.filter(terminal_type=terminal_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["type_filter"] = self.request.GET.get("type", "")
        context["terminal_types"] = Terminal.TERMINAL_TYPE_CHOICES
        return context


class TerminalDetailView(DetailView):
    model = Terminal
    template_name = "terminals/detail.html"
    context_object_name = "terminal"


# Admin CRUD Views
class TerminalCreateView(AdminRequiredMixin, CreateView):
    model = Terminal
    form_class = TerminalForm
    template_name = "terminals/create.html"
    success_url = reverse_lazy("accounts:admin_manage_terminals")

    def form_valid(self, form):
        messages.success(
            self.request, f"Terminal '{form.instance.name}' created successfully!"
        )
        return super().form_valid(form)


class TerminalUpdateView(AdminRequiredMixin, UpdateView):
    model = Terminal
    form_class = TerminalForm
    template_name = "terminals/terminal_form.html"
    context_object_name = "terminal"
    success_url = reverse_lazy("accounts:admin_manage_terminals")

    def form_valid(self, form):
        messages.success(
            self.request, f"Terminal '{form.instance.name}' updated successfully!"
        )
        return super().form_valid(form)


class TerminalDeleteView(AdminRequiredMixin, DeleteView):
    model = Terminal
    template_name = "terminals/confirm_delete.html"
    context_object_name = "terminal"
    success_url = reverse_lazy("accounts:admin_manage_terminals")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(
            request, f"Terminal '{obj.name}' has been deleted successfully!"
        )
        return super().delete(request, *args, **kwargs)
