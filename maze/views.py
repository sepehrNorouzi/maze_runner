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
        """Render the beautiful maze creation form"""
        form = self.form_class()
        context = {
            'form': form,
            'title': 'Create New Maze',
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Handle form submission - currently just pass with comment for future implementation"""
        form = self.form_class(request.POST)

        if form.is_valid():
            w = form.cleaned_data['width']
            h = form.cleaned_data['height']
            mode = form.cleaned_data['algorithm']
            h_p = form.cleaned_data['hybrid_prob']
            m = create_maze(size=w, mode=mode, hybrid_prob=h_p)
            maze = Maze.objects.create(
                creator=request.user,
                height=h,
                width=w,
                growing_tree_algorithm_choice=mode,
                hybrid_prob=h_p
            )
            maze.set_maze_binary(m)
            maze.save()
            messages.success(request, 'Form submitted successfully! Maze creation will be implemented here.')
            return HttpResponseRedirect(reverse('maze-create'))

        else:
            context = {
                'form': form,
                'title': 'Create New Maze',
            }
            return render(request, self.template_name, context)
