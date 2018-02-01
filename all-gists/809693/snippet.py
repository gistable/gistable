'''
WARNINGS: THIS SCRIPT COMES WITHOUT ANY WARRANTY AND RUNNING IT IS DONE SO AT YOUR OWN RISK!
'''
from cms.models import Page

def setup():
    from django.contrib.auth.models import User
    from cms.utils.permissions import set_current_user
    set_current_user(User.objects.get(id=1))
def check_no_moderator():
    print "  checking that CMS_MODERATOR is set to False"
    from django.conf import settings
    if settings.CMS_MODERATOR:
        print "!! Please set CMS_MODERATOR=False in settings before using this script !!"
        print 'aborted'
        raise Exception("!! Please set CMS_MODERATOR=False in settings before using this script !!")



def fix_tree_id():
    setup()
    check_no_moderator()
    print "  rewriting tree_id..."
    #from django.db.models import Avg, Max, Min, Count
    #base_tree_id = Page.objects.filter(parent=None).aggregate(tree_id=Max('tree_id'))['tree_id'] + 1
    base_tree_id = 1
    
    for page in Page.objects.filter(parent=None).order_by('tree_id'):
        page.tree_id = base_tree_id
        page.save()
        r_fix_tree_id(page.children.all(), base_tree_id)
        base_tree_id += 1
def r_fix_tree_id(pages, tree_id):
    for page in pages:
        page.tree_id = tree_id
        page.save(no_signals=True)
        r_fix_tree_id(page.children.all(), tree_id)      

def fix_leftright(do_alteration=True):
    setup()
    check_no_moderator()
    print "  fixing left and right..."
    def recur(node, counter):
        node.lft = counter
        counter += 1
        for child in node.children.all().order_by('tree_id', 'parent', 'lft'):
            counter = recur(child, counter)
        node.rght = counter
        counter += 1
        node.save(no_signals=True)
        return counter
    for root_page in Page.objects.filter(parent=None).order_by('tree_id', 'parent', 'lft'):
        counter = recur(root_page, 1)
        # sanity check
        total_pages = Page.objects.filter(tree_id=root_page.tree_id).count()
        if not total_pages * 2 == counter-1:
            print "            something is wrong! %s != %s" % (total_pages * 2, counter-1)

def fix_level():
    setup()
    print "  fixing level..."
    bad_level_count = 0
    level = 0
    all_pages = Page.objects.order_by('tree_id', 'parent', 'lft')
    for root_page in all_pages.filter(parent=None):
        bad_level_count += r_fix_level(root_page, level=level)
    print "        fixed level of %s pages" % bad_level_count

def r_fix_level(page, level):
    bad_level_count = 0
    if not page.level == level:
        page.level = level
        page.save(no_signals=True)
        bad_level_count += 1
    else:
        pass#print "    comparing level of page id:%s level:%s to level:%s: ok" % (page, page.level, level)
    for subpage in page.children.all():
        bad_level_count += r_fix_level(subpage, level+1)
    return bad_level_count


def fix():
    print "fixing mptt tree"
    fix_tree_id()
    fix_level()
    fix_leftright()
    print "all done"

def check_level():
    print 'Checking levels'
    roots = Page.objects.filter(parent__isnull=True)
    def _rec(pages, level=0):
        for page in pages:
            if page.level != level:
                print 'ERROR: Page %s (%s) has level %s, expected %s' % (page, page.pk, page.level, level)
            children = Page.objects.filter(parent=page)
            _rec(children, level+1)
    _rec(roots)
    print 'Done'
    
def check_leftright():
    print "  checking left and right..."
    errors = {}
    def add_error(node, msg):
        if not node.id in errors.keys():
            errors[node.id] = [u"node: %s" % node]
        errors[node.id].append(msg)
    def recur(node, counter):
        if not node.lft == counter: add_error(node, u"lft is %s, should be %s." % (node.lft, counter))
        counter += 1
        for child in node.children.all().order_by('tree_id', 'parent', 'lft'):
            counter = recur(child, counter)
        if not node.rght == counter: add_error(node, u"rght is %s, should be %s." % (node.rght, counter))
        counter += 1
        return counter
    for root_page in Page.objects.filter(parent=None).order_by('tree_id', 'parent', 'lft'):
        counter = recur(root_page, 1)
        # sanity check
        total_pages = Page.objects.filter(tree_id=root_page.tree_id).count()
        if not total_pages * 2 == counter-1:
            print "            something is wrong! %s != %s" % (total_pages * 2, counter-1)
    from pprint import pprint
    pprint(errors)
    return errors

def kill_moderations():
    from django.db import connection
    HAPPY_MODERATION = """UPDATE cms_page SET moderator_state=10"""
    
    cursor = connection.cursor()
    cursor.execute(HAPPY_MODERATION)
    
            
        