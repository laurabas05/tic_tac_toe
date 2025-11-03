from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Game(models.Model):
    room_name = models.CharField(max_length=50, unique = True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.CharField(max_length=9, default='_'*9)
    active_player = models.IntegerField(default=1)
    STATE_CHOICES = [
        ('active', 'Active'),
        ('won', 'Won'),
        ('tie', 'Tie')
    ]
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='active')
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_games')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.room_name} ({self.state})"