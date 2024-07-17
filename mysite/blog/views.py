from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail, EmailMessage
from .forms import EmailPostForm


# Create your views here.


# def post_list(request):
#     post_published_list = Post.published.all()
#
#     # Добавление пагинации по 3 поста на страницу
#     paginator = Paginator(post_published_list, 3)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#
#     return render(request, 'blog/post/list.html', {'posts': posts})


class PostListView(ListView):
    """
    Альтернативный способ представления списка постов.
    Аналог post_list
    """

    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    return render(request, 'blog/post/detail.html', {'post': post})


def post_share(request, post_id):
    # Извлекаю пост по id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    sent = False

    if request.method == 'POST':
        # Форма передана на обработку
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())

            subject = f'{cd["name"]} рекомендую прочитать {post.title}'
            message = (f'Прочитай {post.title} по ссылке {post_url}\n\n'
                       f'{cd["name"]} комментарии: {cd["comments"]}')

            send_mail(subject, message, 'igor.gass2003@mail.ru', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request,
                  'blog/post/share.html',
                  {
                      'post': post,
                      'form': form,
                      'sent': sent,
                  })
