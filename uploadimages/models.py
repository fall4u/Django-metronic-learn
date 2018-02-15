# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Max


# Create your models here.

class UploadedImage(models.Model):
#	STS_UNBIND = 0
#	STS_BIND   = 1
	image = models.ImageField("Uploaded image")
	isbn  = models.IntegerField()
#	status  = models.IntegerField(default=STS_UNBIND)
	order = models.PositiveIntegerField(editable=False, db_index=True)



	class Meta:
		ordering = ('order',)

	def _swap_qs0(self, qs):
		"""
		Swap the positions of this object with first result, if any, from the provided queryset.
		"""
		try:
		    replacement = qs[0]

		except IndexError:
		    # already first/last
		    return
		self.swap(replacement)

	def swap(self, replacement):
	    """
	    Swap the position of this object with a replacement object.
	    """

	    order, replacement_order = getattr(self, 'order'), getattr(replacement, 'order')
	    print order, replacement_order
	    setattr(self, 'order', replacement_order)
	    setattr(replacement, 'order', order)
	    self.save()
	    replacement.save()

	def down(self,isbn):
		qs = UploadedImage.objects.filter(isbn=isbn)
		self._swap_qs0(qs.filter(**{'order' + '__gt': getattr(self, 'order')}))

	def up(self,isbn):
		qs = UploadedImage.objects.filter(isbn=isbn)
		self._swap_qs0(qs.filter(**{'order' + '__lt': getattr(self, 'order')}))

	def save(self, *args, **kwargs):
	    if getattr(self, 'order') is None:
	        qs = UploadedImage.objects.all()
	        print qs.count()
	        dic = qs.aggregate(Max('order'))
	        print dic

	        c = dic.get('order__max')
	        if c is None:
	            setattr(self, 'order', 0)
	        else:
	            setattr(self, 'order', c + 1)
	    super(UploadedImage, self).save(*args, **kwargs)
