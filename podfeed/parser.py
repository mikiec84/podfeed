import feedparser
from time import gmtime, time, mktime
from urllib.request import urlopen
from math import floor
from os.path import join
from logging import getLogger
LOGGER = getLogger('podfeed')

class Episode:
  ''' Episode represents a single entry in the RSS feed containing a link. '''

  CHUNK_SIZE = 32*1024

  def __init__(self, title, date, link):
    self.title = title
    self.date = date
    self.link = link

  def download(self):
    ''' Download this episode and return it as a file-like object '''
    return urlopen(self.link)

  def save(self, path):
    ''' Download this episode and write it to the specified location '''

    filename = "{0}_{1}.mp3".format(self.title, self.date)
    fullpath = join(path, filename)

    with self.download() as response:
      with open(fullpath, "wb") as outfile:
        try:
          LOGGER.info("Writing {0}...".format(fullpath))

          chunk = response.read(self.CHUNK_SIZE)
          while chunk:
            outfile.write(chunk)
            chunk = response.read(self.CHUNK_SIZE)                

        except Exception as err:
          LOGGER.error("Could not write file: {0}".format(err))

  def getLink(self):
    return self.link

  def getTitle(self):
    return self.title

  def getDate(self):
    return self.date

class AbstractFeedParser:
  ''' AbstractFeedParser is a base class used to parse an RSS feed and identify,
      extract, and download MP3 files from it.

      AbstractFeedParser should be subclassed for a specific RSS feed or type of
      feed. '''
  CHUNK_SIZE = 32*1024

  def __init__(self, name, url):
    self.name = name
    self.url = url

  def getNewEpisodes(self, date):
    ''' Gather new episodes for this feed. '''
    LOGGER.debug("Running {0} parser".format(self.name))

    data = feedparser.parse(self.url)

    if self.isValidData(data) == False:
      raise data['bozo_exception']
 
    else:
      entries = data['entries']
      episodes = []

      for entry in entries:
        if self.isNewEntry(entry, date):
          try:
            episode = self.makeEpisode(entry)            
            episodes.append(episode)

          except Exception as e:
            LOGGER.warn("An error occured while parsing an entry. This entry "+
              "will be ignored: {0}".format(e))

      LOGGER.debug("Processed {0} entries".format(len(episodes)))
      return episodes

  def makeEpisode(self, entry):
    ''' Create an Episode object for this entry '''
    time = floor(mktime(entry['updated_parsed']))
    link = self.getMp3Link(entry)

    episode = Episode(self.name, time, link)
    return episode

  def writeResponseToFile(self, response, filename):
    ''' Write this response object to the given filename. '''
    with open(filename, "wb") as outfile:
      LOGGER.info("Writing {0}...".format(filename))

      chunk = response.read(self.CHUNK_SIZE)
      while chunk:
        outfile.write(chunk)
        chunk = response.read(self.CHUNK_SIZE)                

  def saveNewEpisodes(self, date, directory):
    ''' Gather new episodes for this feed. '''
    LOGGER.debug("Running {0} parser...".format(self.name))

    data = feedparser.parse(self.url)

    if self.isValidData(data) == False:
     raise data['bozo_exception']
 
    else:
      entries = data['entries']
      processed = 0

      for entry in entries:
        if self.isNewEntry(entry, date):
          try:
            self.processEntry(entry, directory)
            processed += 1

          except Exception as e:
            LOGGER.warn("An error occured while parsing an entry. This entry "+
              "will be ignored: {0}".format(e))

      LOGGER.debug("Processed {0} entries".format(processed))

  def isNewEntry(self, entry, date):
    ''' Return true if this entry was published after the given date. '''
    published = mktime(entry['published_parsed'])
    return published >= date

  def isValidData(self, data):
    ''' Return true if this data is valid (well-formed) '''
    valid = True

    if(data['bozo'] == 1):
      exception = data['bozo_exception']

      # CharacterEncodingOverride indicates there was a mismatch between the
      # encoding specified in the HTTP header, and the encoding specified in the
      # XML. This is actually fine; feedparser can handle it regardless.
      if(isinstance(exception, feedparser.CharacterEncodingOverride)):
        LOGGER.warn("{0} parser returned inconsistently encoded data".format(
          self.name))

      else:
        valid = False 

    return valid

  def processEntry(self, entry, directory):
    ''' Process this entry and download an MP3 (if available) into the given
        directory. '''
    filename = self.makeFilename(entry, directory)

    mp3_link = self.getMp3Link(entry)
    with urlopen(mp3_link) as response:
      self.writeResponseToFile(response, filename)

  def makeFilename(self, entry, directory):
    ''' Generate a filename for this entry, in the given directory. '''
    time = floor(mktime(entry['updated_parsed']))
    return "{0}/{1}_{2}.mp3".format(directory, self.name, time)

  def writeResponseToFile(self, response, filename):
    ''' Write this response object to the given filename. '''
    with open(filename, "wb") as outfile:
      LOGGER.info("Writing {0}...".format(filename))

      chunk = response.read(self.CHUNK_SIZE)
      while chunk:
        outfile.write(chunk)
        chunk = response.read(self.CHUNK_SIZE)                

  def getName(self):
    return self.name

  def getMp3Link(self, entry):
    ''' Extract a link to an MP3 file from this entry.
        This method should be overwritten by all child classes. '''
    raise NotImplementedError("AbstractFeedParser.getMp3Link() "+
      "should be overriden for parent classes!")