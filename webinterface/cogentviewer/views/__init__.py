def view_root(context, request):
    return {'items':[1,2], 'project':'orbit_viewer'}

def view_model(context, request):
    return {'item':context, 'project':'orbit_viewer'}
