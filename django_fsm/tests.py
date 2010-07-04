#-*- coding: utf-8 -*-
# pylint: disable=C0111, C0103, R0904

from django.test import TestCase
from django.db import models

from django_fsm.db.fields import FSMField, FSMKeyField, transition

class BlogPost(models.Model):
    state = FSMField(default='new')

    @transition(source='new', target='published')
    def publish(self):
        pass

    @transition(source='published', target='hidden')
    def hide(self):
        pass

    @transition(source='new', target='removed')
    def remove(self):
        raise Exception('No rights to delete %s' % self)

    @transition(source=['published','hidden'], target='stolen')
    def steal(self):
        pass


class FSMFieldTest(TestCase):
    def setUp(self):
        self.model = BlogPost()

    def test_initial_state_instatiated(self):
        self.assertEqual(self.model.state, 'new')

    def test_known_transition_should_succeed(self):
        self.model.publish()
        self.assertEqual(self.model.state, 'published')

        self.model.hide()
        self.assertEqual(self.model.state, 'hidden')

    def test_unknow_transition_fails(self):
        self.assertRaises(NotImplementedError, self.model.hide)

    def test_state_non_changed_after_fail(self):
        self.assertRaises(Exception, self.model.remove)
        self.assertEqual(self.model.state, 'new')

    def test_mutiple_source_support_path_1_works(self):
        self.model.publish()
        self.model.steal()
        self.assertEqual(self.model.state, 'stolen')

    def test_mutiple_source_support_path_2_works(self):
        self.model.publish()
        self.model.hide()
        self.model.steal()
        self.assertEqual(self.model.state, 'stolen')


class InvalidModel(models.Model):
    state = FSMField(default='new')
    action = FSMField(default='no')

    @transition(source='new', target='no')
    def validate(self):
        pass


class InvalidModelTest(TestCase):
    def test_two_fsmfields_in_one_model_not_allowed(self):
        model = InvalidModel()
        self.assertRaises(TypeError, model.validate)


class Document(models.Model):
    status = FSMField(default='new')

    @transition(source='new', target='published')
    def publish(self):
        pass


class DocumentTest(TestCase):
    def test_any_state_field_name_allowed(self):
        model = Document()
        model.publish()
        self.assertEqual(model.status, 'published')


class BlogPostStatus(models.Model):
    name = models.CharField(max_length=3, unique=True)
    objects = models.Manager()

    @transition(source='new', target='published')
    def publish(self):
        pass


class BlogPostWithFKState(models.Model):
    status = FSMKeyField(BlogPostStatus, default='new')

    @transition(source='new', target='published')
    def publish(self):
        pass
 
    @transition(source='published', target='hidden', save=True)
    def hide(self):
        pass


class BlogPostWithFKStateTest(TestCase):
    def setUp(self):
        self.model = BlogPost()
        BlogPostStatus.objects.create(name="new")
        BlogPostStatus.objects.create(name="published")
        BlogPostStatus.objects.create(name="hidden")

    def test_known_transition_should_succeed(self):
        self.model.publish()
        self.assertEqual(self.model.state, 'published')

        self.model.hide()
        self.assertEqual(self.model.state, 'hidden')

    def test_unknow_transition_fails(self):
        self.assertRaises(NotImplementedError, self.model.hide)

