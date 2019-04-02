import logging
import os
from collections import namedtuple
import time
import magic
from io import BytesIO

from django.views.generic import DetailView
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot
import aplpy
import astropy

from scheduler.models import Workflow

astropy.log.setLevel('ERROR')
logger = logging.getLogger(__name__)
filemagic = magic.Magic()  # flags=magic.MAGIC_MIME_TYPE)


class FitsView(DetailView):
    """
    Returns an rendered image. uses path keyword argument. Only
    allowes files which are in te settings.RESULTS_DIR folder somewhere.
    """
    model = Workflow

    def render_to_response(self, context, **kwargs):

        size = int(self.request.GET.get('size', 5))
        vmin = float(self.request.GET.get('vmin', 0))
        vmax = float(self.request.GET.get('vmax', 0.1))
        colorbar = (self.request.GET.get('colorbar', 'True').lower() != 'false')

        fullpath = self.object.get_result(self.kwargs['path'])

        figure = matplotlib.pyplot.figure(figsize=(size, size))

        if colorbar:
            subplot = [0.0, 0.0, 0.9, 1]
        else:
            subplot = [0.0, 0.0, 1, 1]

        try:
            fig = aplpy.FITSFigure(str(fullpath),
                                   figure=figure,
                                   subplot=subplot,
                                   figsize=(size, size))
        except IOError as e:
            matplotlib.pyplot.text(0.1, 0.8, str(e))
        else:
            fig.show_colorscale(vmin=vmin, vmax=vmax)
            if colorbar:
                fig.add_colorbar()
                fig.colorbar.set_font(size='xx-small')
            fig.axis_labels.hide()
            fig.tick_labels.hide()
            fig.ticks.hide()
        buf = BytesIO()
        figure.canvas.print_figure(buf, format='png')
        return HttpResponse(buf.getvalue(), content_type='image/png')


DirItem = namedtuple('DirItem', ['fullpath', 'name', 'type', 'size',
                                 'modified', 'is_image'])


class OverView(DetailView):
    model = Workflow
    template_name = 'viewer/overview.html'

    def get_context_data(self, **kwargs):
        context = super(OverView, self).get_context_data(**kwargs)

        images = []
        dirlist = []
        for result in self.object.results():
            type_ = filemagic.id_filename(str(result))
            size = result.stat().st_size
            modified = time.ctime(os.path.getmtime(result))
            is_image = type_.startswith('FITS image data') or \
                       type_.startswith('PNG image data') or \
                       type_.startswith('JPEG image data')
            if is_image:
                images.append(result)
            dirlist += [DirItem(str(result), result.name, type_, size, modified, is_image)]

        context['dirlist'] = dirlist
        context['images'] = images
        return context


class SomethingView(DetailView):
    """
    Will redirect to correct view according to file type.

    Will render error page if file type is not understood.
    """
    model = Workflow
    template_name = 'viewer/unknowntype.html'

    def get_context_data(self, **kwargs):
        context = super(SomethingView, self).get_context_data(**kwargs)
        fullpath = self.object.get_result(self.kwargs['path'])
        context['type'] = filemagic.id_filename(str(fullpath))
        context['path'] = self.kwargs['path']
        return context

    def render_to_response(self, context, **response_kwargs):
        type_ = context['type']
        if type_.startswith("FITS image data"):
            return HttpResponseRedirect(reverse('scheduler:viewer_fits',
                                                kwargs={'pk': self.object.id,
                                                        'path': self.kwargs['path']}))
        if type_.startswith("ASCII text") or type_.startswith('UTF-8 Unicode text'):
            return HttpResponseRedirect(reverse('scheduler:viewer_text',
                                                kwargs={'pk': self.object.id,
                                                        'path': self.kwargs['path']}))
        if type_.startswith('PNG image data') or type_.startswith('JPEG image data'):
            return HttpResponseRedirect('/'.join([settings.MEDIA_URL,
                                                  self.object.results_dir,
                                                  self.kwargs['path']]))

        return super(SomethingView, self).render_to_response(context)


class TextView(DetailView):
    model = Workflow
    template_name = 'viewer/textfile.html'

    def get_context_data(self, **kwargs):
        context = super(TextView, self).get_context_data(**kwargs)
        path = self.kwargs['path']
        fullpath = str(self.object.outdir())

        with open(fullpath, 'r') as f:
            context['path'] = path
            context['content'] = ''.join(f.readlines())
        return context


class Js9View(DetailView):
    """
    Will redirect to correct view according to file type.

    Will render error page if file type is not understood.
    """
    model = Workflow
    template_name = 'viewer/js9.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['path'] = self.object.outdir() / self.kwargs['path']
        return context
