from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from MainApp.forms import SnippetForm

from MainApp.models import Snippet
from django.contrib import auth


def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)


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
            form.save()  # create and save Snippet's instance
            # GET /snippets/list
            return redirect("snippets-list")  # URL для списка сниппетов
        return render(request, "pages/add_snippet.html", context={"form": form})


def snippets_page(request):
    snippets = Snippet.objects.all()
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
        return render(request, "pages/snippet_detail.html", context)

def snippet_delete(request, snippet_id):
    #snippet = Snippet.objects.get(id=snippet_id)
    #res = Snippet.objects.filter(id=snippet_id).delete()
    if request.method =="GET" or request.method =="POST":
        snippet = get_object_or_404(Snippet,id=snippet_id)
        snippet.delete()
    return redirect("snippets-list")  # URL для списка сниппетов


def snippet_edit(request, snippet_id):
    context = {"pagename": "Редактирование сниппета"}
    snippet = get_object_or_404(Snippet,id=snippet_id)
    if request.method == 'GET':
       form = SnippetForm(instance=snippet)
       context["form"] = form
       return render(request, 'pages/add_snippet.html', context)
    elif request.method == 'POST':
        data_form = request.POST
        #for key,
        snippet.name = data_form["name"]
        snippet.code = data_form["code"]
        snippet.save()
    #     form = SnippetForm(request.POST, instance=snippet)
    #     if form.is_valid():
    #         form.save()
    # else:
    #     pass

    return redirect("snippets-list")  # URL для списка сниппетов

def snippet_search(request):
    snippet_id = request.Get.get("snippet_id")
    if snippet_id:
        return redirect("snippet-detail", snippet_id=snippet_id)
    
def login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        print("username =", username)
        print("password =", password)
        return redirect('home')


def logout(request):
    auth.logout(request)
    return redirect('home')