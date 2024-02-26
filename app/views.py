from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Post, Comments, Tag, Profile, WebsiteMeta
from .forms import CommentForm, SubscribeForm, NewUserForm, PostForm
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db.models import F

# Create your views here.

def subscribe_logic(request):
    subscribe_message = None
    if 'subscribed' in request.session:
        subscribe_message = "You're Already Subscribed"
    elif request.POST:
        subscribe_form = SubscribeForm(request.POST)
        if subscribe_form.is_valid():
            subscribe_form.save()
            request.session['subscribed']=True
            subscribe_message = "Subscribed Successfully"
        else: 
            return subscribe_form.errors
    return subscribe_message

def index(request):
    posts = Post.objects.all()
    top_posts = Post.objects.all().order_by('-view_count')[0:3]
    recent_posts = Post.objects.all().order_by('last_update')[0:3]
    subscribe_form = SubscribeForm()
    featured_blog = Post.objects.filter(is_featured=True)
    website_info = None
    
    if WebsiteMeta.objects.all().exists():
        website_info = WebsiteMeta.objects.all()[0]
    
    if featured_blog:
        featured_blog=featured_blog[0]
    
    subscribe_message=subscribe_logic(request)
    email = request.POST.get('email')
    
    context = {
    'posts':posts,
    'top_posts':top_posts,
    'recent_posts':recent_posts,
    'subscribe_form':subscribe_form,
    'subscribe_message': subscribe_message,
    'featured_blog':featured_blog,
    'website_info':website_info,
    'email':email,
    }
    
    return render(request, 'app/index.html', context)

def post_page(request, slug):
    if Post.objects.get(slug=slug).view_count is None:
        Post.objects.filter(slug=slug).update(view_count=1)
    else:
        Post.objects.filter(slug=slug).update(view_count=F('view_count') + 1)
        
    post = Post.objects.annotate(like_count=Count('likes')).get(slug=slug)
    comments = Comments.objects.filter(post=post)
    form = CommentForm()
    
    subscribe_form = SubscribeForm()
    subscribe_message=subscribe_logic(request)

    
    # Bookmark logic
    is_bookmarked=False
    if post.bookmarks.filter(id=request.user.id).exists():
        is_bookmarked=True
        
    # Like logic
    is_liked=False
    if post.likes.filter(id=request.user.id).exists():
        is_liked=True
    
    if request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            parent_obj = None
            # check if it is a reply being posted
            if request.POST.get('parent'):
                parent = request.POST.get('parent')
                parent_obj = Comments.objects.get(id=parent)
                if parent_obj:
                    comment_reply = comment_form.save(commit=False)
                    comment_reply.parent = parent_obj
                    comment_reply.post=post
                    comment_reply.save()
                    return HttpResponseRedirect(reverse('post_page', kwargs={'slug':slug}))
            else:
                # commit=False allows you to add fields to the object before saving to database
                # we can still alter the below object before saving
                comment = comment_form.save(commit=False)
                post_id = request.POST.get('post_id')
                post = Post.objects.get(id=post_id)
                comment.post = post
                comment.save()
                
                # we do this so we return to the original post 
                    # and a user cant post multiple comments by refreshing the post
                return HttpResponseRedirect(reverse('post_page', kwargs={'slug':slug}))          
            
    # post.save()
    
    # Sidebar logic
    recent_posts = Post.objects.exclude(slug=slug).order_by("-last_update")[0:3]
    top_authors = User.objects.annotate(number=Count('post')).filter(number__gt=0).order_by("-number")
    tags = Tag.objects.all()
    related_posts = Post.objects.exclude(slug=slug).filter(author=post.author)
    
    context = {
        'post':post,
        'form':form,
        'comments':comments,
        'is_bookmarked':is_bookmarked,
        'is_liked':is_liked,
        'recent_posts':recent_posts,
        'top_authors':top_authors,
        'tags':tags,
        'related_posts':related_posts,
        'subscribe_form':subscribe_form,
        'subscribe_message':subscribe_message
        
    }
    
    return render(request, 'app/post.html', context)

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    # get all posts that are associated with this tag then order
    top_posts = Post.objects.filter(tags__in=[tag.id]).order_by('-view_count')[0:2]
    recent_posts = Post.objects.filter(tags__in=[tag.id]).order_by('-last_update')[0:2]
    tags = Tag.objects.all()
    subscribe_form = SubscribeForm()
    subscribe_message=subscribe_logic(request)
    
    context={
        'tag':tag,
        'top_posts':top_posts,
        'recent_posts':recent_posts,
        'tags':tags,
        'subscribe_form':subscribe_form,
        'subscribe_message':subscribe_message
    }
    
    return render(request, 'app/tag.html', context)

def author_page(request, slug):
    author = Profile.objects.get(slug=slug)
    top_posts = Post.objects.filter(author=author.user).order_by('-view_count')[0:2]
    recent_posts = Post.objects.filter(author=author.user).order_by('-last_update')[0:2]
    featured_posts =  Post.objects.filter(author=author.user).filter(is_featured=True)
    top_authors = User.objects.annotate(number=Count('post')).filter(number__gt=0).order_by('number')
    
    subscribe_form = SubscribeForm()
    subscribe_message=subscribe_logic(request)
    
    context = {
        'author':author,
        'top_posts':top_posts,
        'recent_posts':recent_posts,
        'featured_posts':featured_posts,
        'top_authors':top_authors,
        'subscribe_form':subscribe_form,
        'subscribe_message':subscribe_message
    }
    
    return render(request, 'app/author.html', context)

def search_post(request):
    search_query = ''
    # check if the get request has the parameter 'q', defined in the template
    if request.GET.get('q'):
        search_query = request.GET.get('q')
    posts = Post.objects.filter(title__icontains=search_query)
    subscribe_form = SubscribeForm()
    subscribe_message=subscribe_logic(request)
    
    context={
        'posts':posts, 
        'search_query': search_query,
        'subscribe_form':subscribe_form,
        'subscribe_message':subscribe_message
        }
    return render(request, 'app/search.html', context)

def about(request):
    website_info = None
    if WebsiteMeta.objects.all().exists():
        website_info = WebsiteMeta.objects.all()[0]
    subscribe_form = SubscribeForm()
    subscribe_message=subscribe_logic(request)
        
    context={
        'website_info':website_info,
        'subscribe_form':subscribe_form,
        'subscribe_message':subscribe_message
    }
    return render(request, 'app/about.html', context)

def register_user(request):
    form = NewUserForm()
    if request.method=="POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user=form.save()
            # in-built function to authenticate the user and log them in
            login(request, user)
            return redirect('/')
    subscribe_form = SubscribeForm()
    subscribe_message=subscribe_logic(request)
    context={
        'form':form,
        'subscribe_form':subscribe_form,
        'subscribe_message':subscribe_message
        }
    return render(request, 'registration/registration.html', context)

def bookmark_post(request, slug):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    if post.bookmarks.filter(id=request.user.id).exists():
        post.bookmarks.remove(request.user)
    else:
        post.bookmarks.add(request.user)
    
    return HttpResponseRedirect(reverse('post_page', args=[str(slug)]))

def like_post(request, slug):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    
    return HttpResponseRedirect(reverse('post_page', args=[str(slug)]))

def all_posts(request):
    search_query=''
    if request.GET:
        search_query = request.GET.get('q')
    posts = Post.objects.filter(title__contains=search_query)
    subscribe_form = SubscribeForm()
    subscribe_message=subscribe_logic(request)
    
    context={
        'posts':posts,
        'search_query':search_query,
        'subscribe_form':subscribe_form,
        'subscribe_message':subscribe_message
    }
    
    return render(request,'app/all_posts.html', context)

def author_posts(request):
    search_query=''
    if request.GET:
        search_query = request.GET.get('q')
    posts = Post.objects.filter(author=request.user).filter(title__contains=search_query)
    subscribe_form = SubscribeForm()
    subscribe_message=subscribe_logic(request)
    
    context={
        'posts':posts,
        'search_query':search_query,
        'subscribe_form':subscribe_form,
        'subscribe_message':subscribe_message
    }
    
    return render(request,'app/all_posts.html', context)

def all_bookmarked_posts(request):
    search_query=''
    if request.GET:
        search_query = request.GET.get('q')
    all_bookmarked_posts = Post.objects.filter(bookmarks=request.user).filter(title__contains=search_query)
    subscribe_form = SubscribeForm()
    subscribe_message=subscribe_logic(request)
    title = "Bookmarks"
    
    context={
        'posts':all_bookmarked_posts,
        'search_query':search_query,
        'subscribe_form':subscribe_form,
        'subscribe_message':subscribe_message,
        'title':title,
    }
    
    return render(request, 'app/all_posts.html', context)

def all_liked_posts(request):
    search_query=''
    if request.GET:
        search_query = request.GET.get('q')
    all_liked_posts = Post.objects.filter(likes=request.user).filter(title__contains=search_query)
    title = "Likes"
    subscribe_form = SubscribeForm()
    subscribe_message=subscribe_logic(request)
    context = {
        'posts':all_liked_posts,
        'search_query':search_query,
        'title': title,
        'subscribe_form':subscribe_form,
        'subscribe_message':subscribe_message
    }
    
    return render(request, 'app/all_posts.html', context)

def create_post(request):
    if request.GET.get('id'):
        print(request.GET.get('id'))
    tags=[]
    subscribe_form = SubscribeForm()
    subscribe_message=subscribe_logic(request)
    if request.user.is_authenticated:
        if request.GET.get('id'):
            instance = Post.objects.get(id=request.GET.get('id'))
            if request.user!=Post.objects.get(id=request.GET.get('id')).author:
                return HttpResponseRedirect(reverse('create_post'))
            post_form = PostForm(instance=instance)
            if request.POST:
                post_form = PostForm(request.POST, request.FILES, instance=instance)
                if post_form.is_valid():
                    post_form.save()
                    return HttpResponseRedirect(reverse('post_page', args=[instance.slug]))
            
        else:
            post_form = PostForm()
        
            if request.POST:
                # logic to handle submission of post
                post_form = PostForm(request.POST, request.FILES)
                if post_form.is_valid():

                    post = post_form.save(commit=False)
                    print(request.POST.getlist('tags'))
                    tag_ids = request.POST.getlist('tags')
                    tags=Tag.objects.filter(id__in=tag_ids)
                    
                    post.author = request.user
                    post.save()
                    post.tags.set(tags)
                    # post.save()
                    return HttpResponseRedirect(reverse('post_page', args=[post.slug]))
            
        context={
            'post_form':post_form,
            'subscribe_form':subscribe_form,
            'subscribe_message':subscribe_message
        }
        return render(request,'app/create_post.html', context)
    else:
        context={
            'subscribe_form':subscribe_form,
            'subscribe_message':subscribe_message
        }
        return render(request,'app/not_authenticated.html', context)