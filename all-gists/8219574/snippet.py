import urllib, re, os, urlparse, json, random, sys, getopt, gzip, math, time
from multiprocessing.dummy import Pool as ThreadPool
from cStringIO import StringIO
import Image
 
def download_all_thumbs(ld_num=28,dest_folder="thumbs"):
    
    event_name = 'ludum-dare-%d' % ld_num
    entries_page_url_template = "http://www.ludumdare.com/compo/%s/?action=preview&etype=&start=%%d" % event_name
    
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
        
    pool = ThreadPool()
        
    def get_games_on_page(url):
        r"""return a list of match objects
            action will be in group 1.
            id will be in group 2.  
            url to thumbnail will be in group 3
            game title will be in group 4
            author will be in group 5"""
        entry_re = re.compile(r"<a href='\?action=(\w+)&uid=([0-9]+)'><img src='([^']*)'><div class='title'><i>(.*?)</i></div>(.*?)</a></div>")
        f = urllib.urlopen(url)
        contents = f.read().decode('utf-8','replace')
        f.close()
        return entry_re.findall(contents)
        
    def download_thumb(entry):
        action,uid,thumburl,title,author = entry
        author = author.encode('ascii','replace')
        title = title.encode('ascii','replace')
        ext = os.path.splitext(urlparse.urlparse(thumburl).path)[1] or ".jpg"
        print "\tfound %s %s's game %s"%(uid,author,title)  
        thumbfile = "%s/%s%s"%(dest_folder,uid,ext)
        if not os.path.exists(thumbfile):
            src = urllib.urlopen(thumburl)
            if src.code != 200:
                print "ERROR downloading %s %s's game %s: %s %s"%(uid,author,title,thumburl,src.code)
                thumbfile = None
            else:
                bytes = src.read()
                src.close()
                with open(thumbfile,"w") as dest:
                    dest.write(bytes)
        return (action,uid,thumburl,title,author,thumbfile)
        
    game_matches = []
    game_count = 0
    while True:
        page = entries_page_url_template % (game_count)
        print "%d: getting games on page: %s"%(game_count,page)
        page_matches = get_games_on_page(page)
        if 0==len(page_matches):
            print "done!",len(game_matches),"games found."
            break
        game_count += len(page_matches)
        game_matches.extend(pool.map(download_thumb,page_matches))
    return game_matches
    
class Game:
    def __init__(self,args):
        action, self.uid, self.thumburl, self.title, self.author, self.thumbfile = args
        if not self.thumbfile:
            print "SKIPPING %s: NO THUMBNAIL"%self
            self.img = None
            self.aspect = 0
        else:
            with open(self.thumbfile) as f:
                self.img = Image.open(StringIO(f.read())) # problem with too-many-files-open errors
            if self.img.mode != "RGB":
                print "CONVERTING %s from %s to RGB"%(self,self.img.mode)
                self.img = self.img.convert("RGB")
            self.aspect = float(self.img.size[1])/(self.img.size[0] or 1)
        self.placed = None
    def compute_mse(self,target_data,target_w,target_h,patch_w,patch_h):
        # TODO multiprocessing? or numpy?
        img = self.img.resize((patch_w,patch_h),Image.ANTIALIAS).load()
        self.mse = []
        rows, cols, i = target_h/patch_h, target_w/patch_w, 0
        for y in range(rows):
            yofs = y * patch_h
            for x in range(cols):
                xofs = x * patch_w
                err = 0
                for yy in range(patch_h):
                    for xx in range(patch_w):
                        target = target_data[xofs+xx,yofs+yy]
                        src = img[xx,yy]
                        err += sum((a-b)**2 for a,b in zip(target,src))
                self.mse.append((err,i))
                i += 1
    def __str__(self):
        return "%s %s's game %s"%(self.uid,self.author,self.title)
    
if __name__=="__main__":
    
    opts, args = getopt.getopt(sys.argv[1:],"",
        ("ld-num=","algo=","target-image=","thumb-width=","patch-width="))
    opts = dict(opts)
    ld_num = int(opts.get("--ld-num","29"))
    algo = opts.get("--algo","greedy")
    if algo not in ("greedy","timed","test"):
        sys.exit("unsupported algo %s" % algo)
    if len(args) == 1:
        target_filename = args[0]
    elif args:
        sys.exit("unsupported argument %s" % args[0])
    else:
        target_filename = None
    
    index_file = "%d.json"%ld_num
 
    # thumbs not already downloaded?
    if not os.path.exists(index_file):
        index = download_all_thumbs(ld_num)
        with open(index_file,"w") as out:
            json.dump(index,out)
    else:
        # load the index
        with open(index_file) as index:
            index = json.load(index)
     
    # open all the images
    games = filter(lambda x: x.img,map(Game,index))
    print "loaded %d games for ld %d"%(len(games),ld_num)
 
    # load the target image
    target_imagename = opts.get("--target-image","mona_lisa.jpg")
    target = Image.open(target_imagename)
    print "target image %s is %dx%d"%(target_imagename,target.size[0],target.size[1])
    target_prefix = "%d.%s" % (ld_num, os.path.splitext(os.path.basename(target_imagename))[0])
    
    # work out target size
    thumb_aspect = sum(game.aspect for game in games) / len(games)
    patch_w = int(opts.get("--patch-width","10"))
    patch_h = int(float(patch_w)*thumb_aspect)
    print "patches are %dx%d"%(patch_w,patch_h)
    target_w, target_h = target.size
    target_aspect = float(target_w) / target_h
    cols, rows = 1, 1
    while cols*rows < len(games):
        col_asp = float((cols+1)*patch_w) / (math.ceil(float(len(games)) / (cols+1))*patch_h)
        row_asp = float(cols*patch_w) / (math.ceil(float(len(games)) / cols)*patch_h)
        if abs(col_asp-target_aspect) < abs(row_asp-target_aspect):
            cols += 1
        else:
            rows += 1
    target_w = cols * patch_w
    target_h = rows * patch_h
    print "target is %dx%d tiles, %dx%d pixels"%(cols,rows,target_w,target_h)
    print "there are %d tiles and %d images"%(cols*rows,len(games))
    assert cols and rows
    target_data = target.convert("RGB").resize((target_w,target_h),Image.ANTIALIAS).load()
    
    # compute MSE
    if algo != "test":
        start_time = time.clock()
        mse_file = "%s.mse.json.gz"%target_prefix
        if not os.path.exists(mse_file):
            print "computing Mean Square Error (MSE) for each thumbnail for each tile in the target:"
            for game in games:
                sys.stdout.write(".")
                sys.stdout.flush()
                game.compute_mse(target_data,target_w,target_h,patch_w,patch_h)
            gzip.open(mse_file,"wb",9).write(json.dumps({game.uid:game.mse for game in games}))
        else:
            print "loading MSE matches from file..."
            data = json.loads(gzip.open(mse_file,"rb").read())
            for game in games:
                game.mse = data[game.uid]
        print "took",int(time.clock()-start_time),"seconds"
 
    # work out output size etc
    thumb_w = int(opts.get("--thumb-width","30"))
    thumb_h = int(round(float(thumb_w)*thumb_aspect))
    out_w, out_h = cols*thumb_w, rows*thumb_h
    print "thumbs are %dx%d"%(thumb_w,thumb_h)
    print "output is %dx%d"%(out_w,out_h)
    out = Image.new("RGB",(out_w,out_h))
    
    # place them
    print "%s placement:" % algo
    start_time = time.clock()
    used = {}
    placements = 0
    score = 0
    def place(game,err,xy):
        global placements, score
        x = xy % cols
        y = xy // cols
        game.placed = (x*thumb_w,y*thumb_h)
        used[xy] = (err,game)
        sys.stdout.write(".")
        sys.stdout.flush()
        placements += 1
        score += err
    if algo == "test":
        index = range(len(games))
        random.shuffle(index)
        for i,game in enumerate(games):
            place(game,None,index[i])
    elif algo in ("greedy","timed"):
        print "sorting MSE scores..."
        matches = []
        for game in games:
            for mse in game.mse:
                matches.append((mse[0],mse[1],game))
        matches = sorted(matches)
        print "took",int(time.clock()-start_time),"seconds"
        start_time = time.clock()
        for err, xy, game in matches:
            if game.placed: continue
            if xy in used: continue
            place(game,err,xy)
    else:
        raise Exception("unsupported algo %s" % algo)
    print " ",placements,"placements made in",int(time.clock()-start_time),"seconds, scoring",score
    
    if algo == "timed":
        for game in games:
            game.scores = {xy:err for err,xy in game.mse}
        try:
            start_time = time.clock()
            start_score = score
            placements = 0
            while True:
                src_pos = random.randint(1,cols*rows) - 1
                dest_pos = random.randint(1,cols*rows) - 1
                if src_pos not in used or src_pos == dest_pos:
                    continue
                test = score
                src_err, src = used[src_pos]
                test -= src_err
                test += src.scores[dest_pos]
                if dest_pos in used:
                    dest_err, dest = used[dest_pos]
                    test -= dest_err
                    test += dest.scores[src_pos]
                if test < score:
                    if dest_pos in used:
                        score -= dest_err
                        place(dest,dest.scores[src_pos],src_pos)
                    else:
                        del used[src_pos]
                    score -= src_err
                    place(src,src.scores[dest_pos],dest_pos)
                    assert score == test, (score, test)
        except KeyboardInterrupt:
            pass
        print " ",placements,"improvements made in",int(time.clock()-start_time),"seconds, scoring",score,"(%d improvement)"%(start_score-score)
        
    # actually paste them into the output mosaic
    for game in games:
        if not game.placed:
            print "game %s not placed :("%game
        else:
            out.paste(game.img.resize((thumb_w,thumb_h),Image.ANTIALIAS),game.placed)

    
    # done
    if target_filename:
        target_prefix, target_ext = os.path.splitext(os.path.basename(target_filename))
    else:
        target_prefix += ".%s"%algo
        target_ext = ".jpg"
    print "saving %s%s"%(target_prefix,target_ext)
    out.save("%s%s"%(target_prefix,target_ext))
    print "saving %s.idx.json"%target_prefix
    json.dump({game.uid:game.placed for game in games},open("%s.idx.json"%target_prefix,"w"))