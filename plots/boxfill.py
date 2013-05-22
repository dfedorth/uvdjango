import cdms2
from fcntl import flock, LOCK_EX, LOCK_UN
import os
import pycurl
import sys
from urllib import urlencode
import vcs

from util.sanitize import sanitize_filename

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Context, loader, RequestContext
from django.conf import settings
if not settings.configured:
    settings.configure()
    
def boxfill(request):
    '''
    Makes sure a user is authenticated, then draws a boxfill for them.
    '''
    if not request.user.is_authenticated():
        # send them to the login page, with a ?redir= on the end pointing back to this page
        return HttpResponseRedirect(reverse('login:login') + "?" + urlencode({'redir':reverse('home.views.boxfill')}))
    else:
        if request.GET:
            return render(request, 'boxfill_form.html', { })
        else:
            try:
                in_file=request.POST['file']
                selected_var=request.POST['var']
                latitude_from=int(request.POST['latitude_from'])
                latitude_to=int(request.POST['latitude_to'])
                longitude_from=int(request.POST['longitude_from'])
                longitude_to=int(request.POST['longitude_to'])
                time_slice_from=int(request.POST['time_slice_from'])
                time_slice_to=int(request.POST['time_slice_to'])
                lev1=None
                lev2=None
                if 'lev1' in request.POST:
                    lev1=request.POST['lev1']
                if 'lev2' in request.POST:
                    lev2=request.POST['lev2']
            except:
                return render(request, 'boxfill_form.html', {
                    'error_message': "Please fill all required fields",
                })
        
            selection_dict = {
                'latitude':(latitude_from,latitude_to),
                'longitude':(longitude_from,longitude_to),
                'time':slice(time_slice_from,time_slice_to)
            }
               
            # tell curl what certificate to use
            #TODO: sanitize request.user.name!
            current_httprc = settings.PROXY_CERT_DIR + request.user.username + '.httprc'
            
            plot_filename = _vcs_boxfill(in_file, selected_var, selection_dict, httprc = current_httprc)
            
            
            
            return render(request, 'boxfill.html', {
                'png': plot_filename,
            })

def _vcs_boxfill(in_file, selected_var, selection_dict, lev1 = None, lev2 = None, httprc = None):
    '''
    Generates a boxfill plot of the selected variable using vcs.
    Writes a .png file to disk and returns the URL to it when it's done.
    '''
    ### determine the filename plot will have ###
    filename = "plot-boxfill_%s_%s_%s_%s_%s" % (in_file, selected_var, str(selection_dict), lev1, lev2)
    filename = sanitize_filename(filename)
    filename += ".png"
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    
    ### check to see if we've already created this file ###
    if(os.path.isfile(filepath)):
        return settings.MEDIA_URL + filename
    
    ### if not, create the plot, write it to file, and return ###
    try:
        #######################################################################
        # Unidata is adding functionality to netcdf so that we will be able
        # to specify which .dodsrc (or .httprc) file it should read in order
        # to find where the certificate is located.
        # Once they're done with that, we'll need to make some changes to cdms2
        # but in the end, our cdms2 call will probably look something like:
        #
        # httprc_path = settings.PROXY_CERT_DIR + '/' + username + '.httprc')
        # data = cdms2.open(in_file, httprc=httprc_path)
        #######################################################################
        data = cdms2.open(in_file)
        selection = data(selected_var, **selection_dict)
        canvas = vcs.init()
        plot = canvas.createboxfill()
        if lev1 is not None and lev2 is not None:
            plot.level_1 = lev1
            plot.level_2 = lev2
        canvas.clear()
        canvas.plot(selection, plot, bg=1, ratio='autot') # plots in background
        
        with open(filepath, 'wb') as outfile:
            flock(outfile, LOCK_EX)
            canvas.png(filepath)
            flock(outfile, LOCK_UN)
        return settings.MEDIA_URL + filename
    except Exception as e:
        print type(e)
        print "An exception has occured in plots.boxfill()! The error was \"%s\"" % e
        return None
