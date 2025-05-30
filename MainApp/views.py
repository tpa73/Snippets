from django.shortcuts import get_object_or_404, render, redirect
from MainApp.forms import SnippetForm, UserRegistrationForm, CommentForm
from MainApp.models import Snippet
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from http import HTTPStatus

def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)


@login_required(login_url='home')
def my_snippets(request):
    snippets = Snippet.objects.filter(user=request.user)
    context = {
        'pagename': 'Просмотр сниппетов',
        'snippets': snippets,
        }
    
    return render(request, 'pages/view_snippets.html', context)


@login_required
def add_snippet_page(request):
    # Создаем пустую форму при запросе GET
    if request.method == "GET":
        form = SnippetForm()
        context = {
            'pagename': 'Добавление нового сниппета',
            'form': form
            }
        return render(request, 'pages/add_snippet.html', context)

    # Получаем данные из формы и на их основе создаем новый сниппет, сохраняя его в БД
    if request.method == "POST":
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)  # создаем Snippet's instance, но не сохраняем в БД
            if request.user.is_authenticated:
                snippet.user = request.user
                snippet.save()  # Здесь сохраняем
            # GET /snippets/list
            return redirect("snippets-list")  # URL для списка сниппетов
        return render(request, "pages/add_snippet.html", context={"form": form})


def snippets_page(request):
    snippets = Snippet.objects.filter(public=True)
    context = {
        'pagename': 'Просмотр сниппетов',
        'snippets': snippets,
        }
    
    return render(request, 'pages/view_snippets.html', context)


def snippet_detail(request, snippet_id):
    """ Get snippet by id """
    context = {"pagename": "Просмотр сниппета"}
    try:
        snippet = Snippet.objects.get(id=snippet_id)
    except Snippet.DoesNotExist:
        return render(
            request, 
            "pages/errors.html", 
            context | {"error": f"Сниппет с id={snippet_id} не найден."},
            status=404
            )
    else:
        context["snippet"] = snippet
        context["comment_form"] = CommentForm()
        return render(request, "pages/snippet_detail.html", context)


@login_required
def snippet_delete(request, snippet_id):
    if request.method == "GET" or request.method == "POST":
        # Найти snippet по snipped_id или вернуть ошибку 404
        snippet = get_object_or_404(Snippet.objects.filter(user=request.user), id=snippet_id)
        snippet.delete()  # Удаляем snippet из БД

    return redirect("snippets-list")


@login_required
def snippet_edit(request, snippet_id):
    """ Edit snippet by id"""
    context = {"pagename": "Обновление сниппета"}

    # Получить сниппет из БД
    snippet = get_object_or_404(Snippet.objects.filter(user=request.user), id=snippet_id)

    # Создаем форму на основе данных snippet'a при запросе GET
    # Используем параметр instance: SnippetForm(instance=...)
    if request.method == 'GET':
       form = SnippetForm(instance=snippet)
       context["form"] = form
       return render(request, 'pages/add_snippet.html', context)

    # Получаем данные из формы и на их основе обновляем атрибуты snippet'a, сохраняя его в БД
    # Variant 1
    # if request.method == 'POST':
    #     form = SnippetForm(request.POST, instance=snippet)
    #     if form.is_valid():
    #         form.save()
    #         return redirect("snippets-list")  # URL для списка сниппетов
    #     return render(request, "pages/add_snippet.html", context={"form": form})
    
    # Variant 2
    if request.method == "POST":
        data_form = request.POST
         # Универсальный случай
        for key_as_attr, value in data_form.items():
            setattr(snippet, key_as_attr, value)
        snippet.public = data_form.get("public", False)
        # Частный случай
        # snippet.name = data_form["name"]
        # snippet.code = data_form["code"]
        snippet.save()
        return redirect("snippets-list")  # URL для списка сниппетов
    

def snippet_search(request):
    # print(f'{request.path = }')
    # print(f'{request.get_full_path() = }')
    # print(f'{request.GET = }')
    search_snippet_id = request.GET.get("snippet_id")
    if search_snippet_id:
        return redirect("snippet-detail", snippet_id=search_snippet_id)

    return render(
            request, 
            "pages/errors.html", 
            context = {
                "error": f"Сниппет с id={search_snippet_id} не найден.",
                "pagename": "Просмотр сниппета",
                },
            status=404
            )
    

def login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
        else:
            # Return error message
            context = {
                "pagename": "PythonBin",
                "errors": ["Wrong username or password"]
            }
            return render(request, "pages/index.html", context)
    return redirect('home')


def logout(request):
    auth.logout(request)
    return redirect('home')


def create_user(request):
    context = {'pagename': 'Регистрация нового пользователя'}
    # Создаем пустую форму при запросе GET
    if request.method == "GET":
        form = UserRegistrationForm()

    # Получаем данные из формы, валидируем и на их основе создаем нового пользователя, сохраняя его в БД
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")

    context["form"] = form
    return render(request, 'pages/registration.html', context)


@login_required
def create_comment(request):
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            snippet_id = request.POST.get("snippet_id")
            snippet = Snippet.objects.get(id=snippet_id)
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.snippet = snippet
            comment.save()
            # URL path snippet_id = form snippet_id
            return redirect("snippet-detail", snippet_id=snippet_id)
    
    return HttpResponse(status=HTTPStatus.NO_CONTENT)