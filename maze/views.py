import time

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View
from maze.models import Maze

from maze.forms import SimpleMazeForm
from maze.utils import create_maze


class MazeCreateView(View):
    template_name = 'admin/maze/maze/generate_maze_form.html'
    form_class = SimpleMazeForm

    def get(self, request):
        form = self.form_class()
        context = {
            'form': form,
            'title': 'Create New Maze',
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            w = form.cleaned_data['width']
            h = form.cleaned_data['height']
            mode = form.cleaned_data['algorithm']
            h_p = form.cleaned_data['hybrid_prob']
            _t0 = time.time_ns()
            maze = Maze.create(creator=request.user, size=w, mode=mode, hybrid_prob=h_p)
            _t1 = time.time_ns()
            messages.success(request, 'Maze created successfully in {} nano seconds'.format(str(_t1 - _t0)))
            return HttpResponseRedirect(reverse('admin:maze_maze_change', args=[maze.id]))

        else:
            context = {
                'form': form,
                'title': 'Create New Maze',
            }
            return render(request, self.template_name, context)
