import django.dispatch

sync_update_signal = django.dispatch.Signal(providing_args=['rv_obj', 'pack_objs'])
