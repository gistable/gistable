import nltk
import requests

FREEBASE_API_KEY = ''

class FindNames(object):

  def __init__(self, text, freebase_api_key):
    self.text = text
    self.key = freebase_api_key
    self.sentences = [sent.strip() for sent in nltk.tokenize.sent_tokenize(self.text)[:]]
    self.freebase_search_url = 'https://www.googleapis.com/freebase/v1/search'
    self.freebase_reconsile_url = 'https://www.googleapis.com/freebase/v1/reconcile'

  def get_named_entities(self):
    '''
    Returns a list of the named entities found in the text
    '''
    named_entities = []
    for sent in self.sentences:
      split = nltk.word_tokenize(sent)
      tokens = nltk.pos_tag(split)
      nes = nltk.chunk.ne_chunk(tokens, binary=True)
      for tok in nes:
        if isinstance(tok, nltk.tree.Tree): #this is named entity!
          if tok.node == 'NE':
            named_entities.append(' '.join(key for key,val in tok.leaves()))
          else:
            print 'Not sure what else...' + tok.node

    #kind of hacky n^2 alg to remove substrings so we don't double search
    setne = list(set(named_entities))
    print named_entities
    print setne
    final_ne = []
    for entity in setne:
      solid = True
      for entity2 in setne:
        if entity != entity2:
          if entity2.find(entity) >= 0:
            #keep if entity isn't a sub string
            solid = False
      if solid:
        final_ne.append(entity)
    return final_ne

  def get_freebase_possibilities(self):
    '''
    Gets the results returned from freebase call.
    '''
    named_entities = self.get_named_entities()
    for ne in named_entities:
      params = {}
      params['query'] = ne
      params['key'] = self.key
      params['filter'] = '(any domain:/american_football)'
      options = requests.get(self.freebase_search_url, params=params).json().get("result", "")
      if options and options[0].get('score') > 10:
        print ne + ': ' + options[0].get('name') + ' ' + str(options[0].get('score'))


def main():
  '''
  Run some tests
  '''
  fn = FindNames(text, FREEBASE_API_KEY)
  fn.get_freebase_possibilities()

if __name__ == '__main__':
  text = '''
Not long ago, Trent Richardson was viewed as a cornerstone for Cleveland's future.

On Wednesday, he became part of its recent inglorious past.

The Browns traded the powerful running back to Indianapolis in a stunning move just two games into the season and one year after drafting Richardson in the first round.

The team's new front office dealt Richardson for a first-round draft pick next year, when the team will have two opening-round selections and 10 overall. Cleveland is rebuilding again and the team hopes to use those picks - seven in the first four rounds - to help turn around a floundering franchise.

Such a reversal was what the Browns had in mind when they took Richardson with the No. 3 overall pick in 2012. The former Alabama standout seemed to have it all: power, speed and good hands.

But Richardson wasn't the kind of back Cleveland's front office wants or apparently suited first-year coach Rob Chudzinski's offense. Richardson, who rushed for 950 yards as a rookie despite playing most of last season with two broken ribs, gained just 105 yards on 31 carries in Cleveland's two losses this season.

He lacked the explosiveness the Browns' new regime was looking for, and it may not have helped that Richardson made it clear he wanted the ball more.

However, Browns CEO Joe Banner said there was nothing negative about Richardson and the team simply seized an opportunity to improve. And the Colts have been looking for a back since Vick Ballard suffered a season-ending knee injury.

''This was more about the moment presented itself,'' Banner said, ''and based on the situation the Colts found themselves in, it wasn't something where we could say, 'Can you wait three weeks to think about this or learn more?' We thought it was a move to make us better and we had to make that decision now. We decided to move forward.''

Banner said the Browns' first conversation with Indianapolis about a deal for Richardson was Tuesday.

The shocking trade - easily the biggest in Cleveland's expansion era and one of the most significant since the Browns joined the NFL in 1950 - came on the same day Chudzinski announced third-string quarterback Brian Hoyer will start Sunday against Minnesota. Hoyer got the surprising nod over backup Jason Campbell to fill in for starter Brandon Weeden, who is sidelined with a sprained right thumb.

The double whammy floored many Browns fans, leaving some to wonder if the team was giving up on this season.

Banner denied that and said he understands the fans' suspicions.

''We have to earn their belief and trust in the decisions we're going to make as a group,'' he said. ''I don't expect them to trust that until we prove that the trust is well placed. So, I understand the skepticism for now. We have to do what we think is right, move the franchise forward and get it to where we want it to be.''

Chudzinski isn't worried about any negative backlash from his players, who had left the facility when the trade was announced.

''That's football,'' said Chudzinski, adding he reached out to the team's captains. ''You deal with those things whether they are injuries or a trade. I believe in this group and I believe the next guy will step up and we will find a way and do what we need to do to win.''

Like Richardson, Weeden's days could be numbered with the Browns, who have started 19 quarterbacks since 1999 and are still looking for the right one. Next year's draft class includes several top-flight QBs and the Browns could be loading up on high picks to make sure they get a good one.

Banner, though, said the Browns aren't angling toward any particular position or player.

''I don't want to tip our hands on what we're going to do or prioritize in doing, but I think it puts us in a very good position to have made some real progress with the team in this offseason to be in very good cap shape going into next season,'' he said.

The Browns are brutally thin at running back after trading Richardson and losing Dion Lewis and Montario Hardesty to season-ending injuries. Chris Ogbonnaya and Bobby Rainey are the only backs on the roster.

The team is bringing in free-agent running back Willis McGahee for a physical and will sign him if he passes the examination. A two-time Pro Bowler, McGahee rushed for 731 yards in 10 games for the Broncos last season and has gained 8,097 in his nine-year career.

Richardson has been slowed by injuries since he was taken after Luck and Robert Griffin III last year.

His college coach, Nick Saban, wished him well with the Colts.

''Hopefully this is going to be a great situation and circumstance for him, so that he can have more success, and be a good player for a long time,'' Saban said. ''The guy was a fantastic player here. We never had anybody who contributed more to the team in terms of how he played and how he affected other people.''

Before the deal, Richardson spoke to Minnesota reporters on a conference call about the expectations that come with being such a high draft pick.

''I think people make it more pressure than what it is,'' he said. ''I just like to play football. At the end of the day, I'm going to play football like I've always been coached. The way I've always played. I'm going to be physical, fast, I'm going to be up-tempo.''

And he's going to do so in a new uniform.
  
  '''
  main()
