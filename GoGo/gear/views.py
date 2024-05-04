from django.urls import reverse_lazy
from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import VueloSearchForm
from .models import Reserva, Vuelo
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)


def home_view(request):
    return render(request, "gear/home.html")


#CRUD: Vuelo

class VueloListView(LoginRequiredMixin, ListView):
    model = Vuelo
    template_name = "gear/vbc/vuelo_list.html"
    context_object_name = "HAWAII"


class VueloDetailView(LoginRequiredMixin, DetailView):
    model = Vuelo
    template_name = "gear/vbc/vuelo_detail.html"
    context_object_name = "TOKYO"


class VueloDeleteView(LoginRequiredMixin, DeleteView):
    model = Vuelo
    template_name = "gear/vbc/vuelo_confirm_delete.html"
    success_url = reverse_lazy("vuelo-list")


class VueloUpdateView(LoginRequiredMixin, UpdateView):
    model = Vuelo
    template_name = "gear/vbc/vuelo_form.html"
    fields = ["nombre", "disponible", "capacidad"]
    context_object_name = "vuelo"
    success_url = reverse_lazy("vuelo-list")


class VueloCreateView(LoginRequiredMixin, CreateView):
    model = Vuelo
    template_name = "gear/vbc/vuelo_form.html"
    fields = ["nombre","tipo", "disponible", "capacidad"]
    success_url = reverse_lazy("vuelo-list")


def vuelo_search_view(request):
    if request.method == "GET":
        form = VueloSearchForm()
        return render(
            request, "gear/form_search.html", context={"search_form": form}
        )
    elif request.method == "POST":
        form = VueloSearchForm(request.POST)
        if form.is_valid():
            nombre_de_vuelo = form.cleaned_data["nombre"]
            descartar_no_disponibles = form.cleaned_data["disponible"]
            capacidad_minima = form.cleaned_data["capacidad_minima"]
            tipo_de_vuelo = form.cleaned_data["tipo_de_vuelo"]

            vuelos_encontradas = Vuelo.objects.filter(nombre__icontains=nombre_de_vuelo)

            if descartar_no_disponibles:
                vuelos_encontradas = vuelos_encontradas.filter( disponible=True)

            if capacidad_minima:
                vuelos_encontradas = vuelos_encontradas.filter(capacidad__gte=capacidad_minima)

            if tipo_de_vuelo:
                vuelos_encontradas = vuelos_encontradas.filter(tipo=tipo_de_vuelo)



            contexto_dict = {"HAWAII": vuelos_encontradas}
            return render(request, "gear/vbc/vuelo_list.html", contexto_dict)
        else:
            return render(
                request, "gear/form_search.html", context={"search_form": form}
            )

#LOGIN/LOGOUT

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm


def user_login_view(request):
    if request.method == "GET":
        form = AuthenticationForm()
    elif request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.user_cache
            if user is not None:
                login(request, user)
                return redirect("home")

    return render(request, "gear/login.html", {"ADMIN": form})


def user_logout_view(request):
    logout(request)
    return redirect("login")

#EDIT USER

from django.contrib.auth.models import User
from .forms import UserEditForm

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'gear/user_edit_form.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user
    
#AVATAR

from .models import Avatar
from .forms import AvatarCreateForm


def avatar_view(request):
    if request.method == "GET":
        contexto = {"NICOLAS": AvatarCreateForm()}
    else:
        form = AvatarCreateForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]
            avatar_existente = Avatar.objects.filter(user=request.user)
            avatar_existente.delete()
            nuevo_avatar = Avatar(image=image, user=request.user)
            nuevo_avatar.save()
            return redirect("home")
        else:
            contexto = {"NICOLAS": form}


    return render(request, "gear/avatar_create.html", context=contexto)
