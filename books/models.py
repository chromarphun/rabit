from django.db import models
from datetime import date

# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length = 50, unique=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        ordering = ['name']


class Book(models.Model):
    title = models.CharField()
    author = models.CharField()
    year = models.IntegerField()
    tags = models.ManyToManyField(Tag, related_name="books")
    def __str__(self):
        return str(self.title)
    class Meta:
        ordering = ['title']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_book'
            )
        ]


class ReadingStatus(models.TextChoices):
    DID_NOT_FINISH = "DNF", "Did Not Finish"
    IN_PROGRESS = "INP", "In Progress"
    COMPLETED = "CMP", "Completed"

class Reading(models.Model):

    book = models.ForeignKey(Book, on_delete = models.CASCADE, related_name="readings")
    start_date = models.DateField()
    end_date = models.DateField()
    asynchronous = models.BooleanField()
    length = models.IntegerField()
    status = models.CharField(max_length = 3, choices = ReadingStatus)
    def __str__(self):
        return f"{str(self.book)} - {str(self.start_date)} to {str(self.end_date)}"
    def save(self, *args, **kwargs):
        days = (self.end_date - self.start_date).days + 1
        self.length = days
        super().save(*args, **kwargs)
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition = (
                    models.Q(
                        asynchronous=True,
                        status__in=[
                            ReadingStatus.IN_PROGRESS,
                            ReadingStatus.COMPLETED
                        ],
                    )
                    | models.Q(
                        asynchronous=False,
                        status__in=[
                            ReadingStatus.DID_NOT_FINISH,
                            ReadingStatus.COMPLETED
                        ],                        
                    )
                ),
                name = "valid_status_based_on_async",
                violation_error_message="Asynchronous readings can only be In Progress or Completed, Synchronous must be DNF or Completed."
            ),
            models.CheckConstraint(
                condition = models.Q(start_date__lte=models.F("end_date")),
                name="start_date_before_end_date",
                violation_error_message="Start date must be before the end date.",
            )
        ]
        ordering = ['start_date']


