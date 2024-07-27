from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import FormMixin

from .forms import *
from .models import *

class Home(ListView):
    model = Movie
    template_name = 'movie_app/home_page.html'
    context_object_name = 'movies'

class Cats(ListView):
    model = Category
    template_name = 'movie_app/cat_list.html'
    context_object_name = 'categories'

class MovieCat(ListView):
    model = Movie
    template_name = 'movie_app/movies_list.html'
    context_object_name = 'movies'

    def get_queryset(self):
        return Movie.objects.filter(category__slug=self.kwargs['cat_slug'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = context['movies'][0].category.title
        return context

class ShowMovie(FormMixin,DetailView):
    form_class = CommentsForm
    model = Movie
    template_name = 'movie_app/movie_detail.html'
    slug_url_kwarg = 'movie_slug'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        context['comments'] = CommentMovie.objects.filter(post=movie)
        return context

    def post(self, request, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.get_object()
        comment.author = self.request.user
        comment.save()
        return super().form_valid(comment)

    def get_success_url(self, **kwargs):
        return reverse_lazy('movie', kwargs={
            'movie_slug': self.kwargs['movie_slug'],
            'cat_slug': self.kwargs['cat_slug'],
        })

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'movie_app/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'movie_app/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход'
        return context

    def get_success_url(self):
        return reverse_lazy('home')

class UserAccount(DetailView):
    model = User
    template_name = 'movie_app/personal_account.html'
    context_object_name = 'user'
    pk_url_kwarg = 'user_pk'

def logout_user(request):
    logout(request)
    return redirect('login')