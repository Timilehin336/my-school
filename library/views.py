from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Book, BookIssue


@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, "library/book_list.html", {"books": books})


@login_required
def my_issues(request):
    profile = getattr(request.user, "student_profile", None)
    issues = BookIssue.objects.filter(student=profile).select_related("book") if profile else []
    return render(request, "library/my_issues.html", {"issues": issues})
