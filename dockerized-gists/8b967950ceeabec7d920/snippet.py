from clarifai.client import ClarifaiApi
import spotipy

class SpotiTags(ClarifaiApi):
    """
    A wrapper to tag spotify album covers from a given artist
    using the Clarifai Deep-learning API.
    
    Requires to set-up the Clarifai API first.
    
    Usage:
      sp = SpotiTags()
      print sp.tag('3jOstUTkEu2JkjvRdBA5Gu')
    """

    # A blacklist of terms that are (generally) not relevant to artists,
    # but generic to the "album cover" artistic concept
    BLACKLIST = [
        'art',
        'artistic',
        'background',
        'design',
        'graphic',
        'graphic design',
        'illustration',
        'painting',
        'portrait',
        'poster',
        'retro',
        'sign',
        'symbol',
        'vector'
    ]
    
    def __init__(self):
        super(SpotiTags, self).__init__()
        self._spotipy = spotipy.Spotify()
        self._cleanup()
        
    def _cleanup(self):
        self._image_tags = {}
        self._tags = {}        

    def _get_covers(self, artist, limit=10):
        """
        Get artist images from the Spotify API.
        
        Removes duplicate and epty results.
        
        Parameters:
        - query: the query string (e.g. 'motorhead')
        - limit: the number of images (optional)
        
        Output:
        - list: a list of distinct image URLs
        """
        albums = self._spotipy.artist_albums(artist).get('items')
        covers = [self._get_largest_image(album['images']) for album in albums]
        covers = list(set(filter(None, covers)))
        return limit < len(covers) and covers[:limit] or covers
      
    def _get_largest_image(self, images):
        """
        Returns the largest Spotify images among the images list.
        
        Parameters:
        - images: a list of images (as Spotify API dicts)
        
        Output:
        - image: A single image, None if no images available
        """
        sorted_images = sorted(images, key=lambda x: x.get('height'), reverse=True)
        return sorted_images and sorted_images[0].get('url') or None

    def _tag(self, images):
        """
        Tag images via the Clarifai API.
        
        Group results as a dict using the image URL as a key, and a dict of
        class => value as the dict value, e.g.
        {
            "http://example.org/foo"  : {
                "bar": 0.65
            }
        }
        
        Parameters:
        - images: a list of images URLs to tag
        
        Output:
        - tags: a dictionary of images URLs and tags (as desribed above)
        """
        tags = {}
        for result in self.tag_image_urls(images)['results']:
            classes = result['result']['tag']['classes']
            prob = result['result']['tag']['probs']
            tags[result['url']] = dict([class_, prob[i]] for (i, class_) in enumerate(classes))
        return tags

    def tag(self, artist):
        """
        Run the whole tagging process.
        
        Aggregates the value of each tag, and return sorted results (most popular first).
        Uses a blacklist of not relevant terms.
    
        parameters:
        - query: the query string, i.e. artist name (e.g. 'motorhead')
        
        Output:
        - tags: a list of (tag, value) items, ordered by most popular tags first
        """
        self._cleanup()
        covers = self._get_covers(artist)
        for cover, tags in self._tag(covers).items():
            for tag, value in tags.items():
                if tag in self.BLACKLIST:
                    continue
                self._tags.setdefault(tag, 0)
                self._tags[tag] += value
        return sorted(self._tags.items(), key=lambda x: x[1], reverse=True)