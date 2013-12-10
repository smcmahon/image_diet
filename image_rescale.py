from Products.Archetypes.Field import ObjectField
from transaction import commit

site = obj
pc = site.portal_catalog

# if an image exceeds these dimensions, it will be checked
max_size = (768, 768)
# if we'd save this much, we'll rescale
margin = 50000
# commit every commit_at writes
commit_at = 100

files_scaled = 0
saved = 0
obj_writes = 0

image_brains = pc(portal_type=('News Item', 'Image'))
for brain in image_brains:
    image = brain.getObject()
    field = image.Schema().get('image')
    value = field.getRaw(image)
    try:
        size = value.getSize()
    except AttributeError:
        print "Skipping %s" % image.absolute_url()
        continue
    if size[0] > max_size[0] or size[1] > max_size[1]:
        factor = min(float(max_size[0]) / float(value.width),
                     float(max_size[1]) / float(value.height))
        w = int(factor * value.width)
        h = int(factor * value.height)
        fvalue, format = field.scale(value.data, w, h)
        data = fvalue.read()
        if len(value.data) > len(data) + margin:
            print image.getId(), value.getSize(), len(value.data), len(data)
            ObjectField.set(field, image, data)
            obj_writes += 1
            if obj_writes >= commit_at:
                print "committing"
                commit()
                obj_writes = 0
            files_scaled += 1
            saved += len(value.data) - len(data)
commit()

print "***********"
print "Files scaled: %s, Bytes saved: %s" % (files_scaled, saved)
