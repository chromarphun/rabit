from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from .models import Book, Reading, Tag, ReadingStatus

# Create your tests here.

class BookTesting(TestCase):
    def setUp(self):
        Book.objects.create(title = "My Title", author = "My Author", year = "2000")
        Book.objects.create(title = "My Title", author = "My Other Author", year = "2000")
    def test_uniqueness_check(self):
        Book.objects.create(title = "My New Title", author = "My Author", year = "2000")
        with self.assertRaises(IntegrityError):
            Book.objects.create(title = "My Title", author = "My Author", year = "2000")

class ReadingTesting(TestCase):
    def setUp(self):
        self.test_book = Book.objects.create(title = "My Title", author = "My Author", year = "2000")
    def test_bad_dates(self):
        with self.assertRaises(IntegrityError):
            Reading.objects.create(book = self.test_book, 
                                   start_date = '2025-10-19', 
                                   end_date = '2025-10-18', 
                                   asynchronous = False, 
                                   status = ReadingStatus.COMPLETED)
    def test_bad_sync_in_progress(self):
        with self.assertRaises(IntegrityError):
            Reading.objects.create(book = self.test_book, 
                                   start_date = '2025-10-19', 
                                   end_date = '2025-10-20', 
                                   asynchronous = False, 
                                   status = ReadingStatus.IN_PROGRESS)
    def test_bad_async_dnf(self):
        with self.assertRaises(IntegrityError):
            Reading.objects.create(book = self.test_book, 
                                   start_date = '2025-10-19', 
                                   end_date = '2025-10-20', 
                                   asynchronous = True, 
                                   status = ReadingStatus.DID_NOT_FINISH)        
    def test_good_reading(self):
            Reading.objects.create(book = self.test_book, 
                                   start_date = '2025-10-19', 
                                   end_date = '2025-10-20', 
                                   asynchronous = False, 
                                   status = ReadingStatus.COMPLETED)

class ReadingPostTesting(TestCase):
    def setUp(self):
        self.url = reverse("books:add_reading")
        self.unread_tag = Tag.objects.create(name="Unread")
        self.rereadable_tag = Tag.objects.create(name="Rereadable")
        self.good_unread = Book.objects.create(title = "My Good Unread Book", author = "My Author", year = "2000")
        self.bad_unread = Book.objects.create(title = "My Bad Unread Book", author = "My Author", year = "2000")
        self.good_previously_read = Book.objects.create(title = "My Good Read Book", author = "My Author", year = "2000")
        self.bad_previously_read = Book.objects.create(title = "My Bad Read Book", author = "My Author", year = "2000")
        self.good_unread.tags.add(self.unread_tag.id)
        self.bad_unread.tags.add(self.unread_tag.id)
        self.good_previously_read.tags.add(self.rereadable_tag)
        self.bad_previously_read.tags.add(self.rereadable_tag)
    def test_good_unread(self):
        payload = {
            "book": self.good_unread.id,
            "start_date": "2025-10-10",
            "end_date": "2025-10-11",
            "asynchronous": False,
            "status": ReadingStatus.COMPLETED,
            "reread_eligible": True
        }
        self.client.post(self.url, data=payload)
        self.assertFalse(self.good_unread.tags.filter(id=self.unread_tag.id).exists())
        self.assertTrue(self.good_unread.tags.filter(id=self.rereadable_tag.id).exists())
    def test_bad_unread(self):
        payload = {
            "book": self.bad_unread.id,
            "start_date": "2025-10-10",
            "end_date": "2025-10-11",
            "asynchronous": False,
            "status": ReadingStatus.DID_NOT_FINISH,
            "reread_eligible": False
        }
        self.client.post(self.url, data=payload)
        self.assertFalse(self.bad_unread.tags.filter(id=self.unread_tag.id).exists())
        self.assertFalse(self.bad_unread.tags.filter(id=self.rereadable_tag.id).exists())
    def test_good_reread(self):
        payload = {
            "book": self.good_previously_read.id,
            "start_date": "2025-10-10",
            "end_date": "2025-10-11",
            "asynchronous": False,
            "status": ReadingStatus.COMPLETED,
            "reread_eligible": True
        }
        self.client.post(self.url, data=payload)
        self.assertFalse(self.good_previously_read.tags.filter(id=self.unread_tag.id).exists())
        self.assertTrue(self.good_previously_read.tags.filter(id=self.rereadable_tag.id).exists())
    def test_bad_reread(self):
        payload = {
            "book": self.bad_previously_read.id,
            "start_date": "2025-10-10",
            "end_date": "2025-10-11",
            "asynchronous": False,
            "status": ReadingStatus.COMPLETED,
            "reread_eligible": False
        }
        self.client.post(self.url, data=payload)
        self.assertFalse(self.bad_previously_read.tags.filter(id=self.unread_tag.id).exists())
        self.assertFalse(self.bad_previously_read.tags.filter(id=self.rereadable_tag.id).exists())
    def test_stay_unread(self):
        payload = {
            "book": self.good_unread.id,
            "start_date": "2025-10-10",
            "end_date": "2025-10-11",
            "asynchronous": True,
            "status": ReadingStatus.IN_PROGRESS,
            "reread_eligible": False
        }
        self.client.post(self.url, data=payload)
        self.assertTrue(self.good_unread.tags.filter(id=self.unread_tag.id).exists())
