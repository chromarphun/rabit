from django.shortcuts import render, get_object_or_404
from django.db.models import Min, Sum
from django.http import HttpResponse
from django.template import loader
from datetime import date

from .models import Book, Tag, Reading, ReadingStatus
from .forms import BookForm, TagForm, ReadingForm

MIN_DATE = '2025-01-01'

def index(request):
    tags = request.GET.getlist('tag')

    booklist = Book.objects.order_by("year")
    for tag in tags:
        booklist = booklist.filter(tags__name=tag)
    tags = Tag.objects.all()
    context = {"booklist": booklist, "tags": tags}
    return render(request, "books/index.html", context)

def summary(request):
    readinglist = Reading.objects.order_by("-end_date")
    today = date.today().isoformat()
    year_start = f"{today[:4]}-01-01"
    status_filters = request.GET.getlist('status')
    for status_filter in status_filters:
        readinglist.filter(status=status_filter)



    async_filter = request.GET.get('async', 'off') == 'on'
    readinglist = readinglist.filter(asynchronous = async_filter)
    start_date_filter = request.GET.get('start_date', MIN_DATE)
    readinglist = readinglist.filter(start_date__gte=start_date_filter)
    end_date_filter = request.GET.get('end_date', today)
    readinglist = readinglist.filter(end_date__lte=end_date_filter)
    
    count = readinglist.count()
    if count != 0:
        total_length = Reading.objects.aggregate(total=Sum("length"))["total"]
        average = f"{(total_length / count):.2f}"
    else:
        average = 0
    context = {
        "readinglist": readinglist,
        "statuses": ReadingStatus.labels,
        "today": today,
        "year_start": year_start,
        "min_date": MIN_DATE,
        "count": count,
        "average": average

    }
    return render(request, "books/summary.html", context)

def detail(request, book_id):
    book = get_object_or_404(Book, pk = book_id)
    return render(request, "books/detail.html", {"book": book})

def add_book(request):
    newform = BookForm()
    new_render = render(request, "books/add.html", {"form": newform, "form_dest": "books:add_book"})
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return new_render
        else:
            return render(request, "books/add.html", {"form": newform, "form_dest": "books:add_reading", "error": form.errors})
    else:
        return new_render

def add_tag(request):
    newform = TagForm()
    new_render = render(request, "books/add.html", {"form": newform, "form_dest": "books:add_tag"})
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return new_render
        else:
            return render(request, "books/add.html", {"form": newform, "form_dest": "books:add_reading", "error": form.non_field_errors})
    else:
        return new_render

def add_reading(request):
    newform = ReadingForm()
    new_render = render(request, "books/add.html", {"form": newform, "form_dest": "books:add_reading"})
    if request.method == "POST":
        form = ReadingForm(request.POST)
        if form.is_valid():
            new_reading = form.save()
            rereadable_tag = Tag.objects.get(name="Rereadable")
            unread_tag = Tag.objects.get(name="Unread")
            if form.cleaned_data.get("status") != ReadingStatus.IN_PROGRESS:
                new_reading.book.tags.remove(unread_tag.id)
            if form.cleaned_data.get("reread_eligible"):
                new_reading.book.tags.add(rereadable_tag.id)
            else:
                new_reading.book.tags.remove(rereadable_tag.id)
            return new_render
        else:
            return render(request, "books/add.html", {"form": newform, "form_dest": "books:add_reading", "error": form.non_field_errors})
    else:
        return new_render

