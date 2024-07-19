from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail, EmailMessage
from .forms import EmailPostForm, CommentForm
from django.views.decorators.http import require_POST
from taggit.models import Tag


# Create your views here.


def post_list(request, tag_slug: str = None):
    post_published_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_published_list = post_published_list.filter(tags__in=[tag])

    # Добавление пагинации по 3 поста на страницу
    paginator = Paginator(post_published_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html',
                  {
                      'posts': posts,
                      'tag': tag,
                  })


# class PostListView(ListView):
#     """
#     Альтернативный способ представления списка постов.
#     Аналог post_list
#     """
#
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_detail(request, year: int, month: int, day: int, post: str):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    # Список активных комментариев к посту
    comments = post.comments.filter(active=True)
    # Форма для комментирования
    form = CommentForm()

    return render(request,
                  'blog/post/detail.html',
                  {
                      'post': post,
                      'comments': comments,
                      'form': form,
                  })


def post_share(request, post_id: int):
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


@require_POST
def post_comment(request, post_id: int):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Создаю объект класса Comment, не сохраняя его в БД
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(request,
                  'blog/post/comment.html',
                  {
                      'post': post,
                      'form': form,
                      'comment': comment,
                  })
