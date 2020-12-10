class InfoExtractor(object):
    """Information Extractor class.
    Information extractors are the classes that, given a URL, extract
    information about the video (or videos) the URL refers to. This
    information includes the real video URL, the video title, author and
    others. The information is stored in a dictionary which is then
    passed to the YoutubeDL. The YoutubeDL processes this
    information possibly downloading the video to the file system, among
    other possible outcomes.
    The type field determines the type of the result.
    By far the most common value (and the default if _type is missing) is
    "video", which indicates a single video.
    For a video, the dictionaries must include the following fields:
    id:             Video identifier.
    title:          Video title, unescaped.
    Additionally, it must contain either a formats entry or a url one:
    formats:        A list of dictionaries for each format available, ordered
                    from worst to best quality.
                    Potential fields:
                    * url        The mandatory URL representing the media:
                                   for plain file media - HTTP URL of this file,
                                   for RTMP - RTMP URL,
                                   for HLS - URL of the M3U8 media playlist,
                                   for HDS - URL of the F4M manifest,
                                   for DASH
                                     - HTTP URL to plain file media (in case of
                                       unfragmented media)
                                     - URL of the MPD manifest or base URL
                                       representing the media if MPD manifest
                                       is parsed from a string (in case of
                                       fragmented media)
                                   for MSS - URL of the ISM manifest.
                    * manifest_url
                                 The URL of the manifest file in case of
                                 fragmented media:
                                   for HLS - URL of the M3U8 master playlist,
                                   for HDS - URL of the F4M manifest,
                                   for DASH - URL of the MPD manifest,
                                   for MSS - URL of the ISM manifest.
                    * ext        Will be calculated from URL if missing
                    * format     A human-readable description of the format
                                 ("mp4 container with h264/opus").
                                 Calculated from the format_id, width, height.
                                 and format_note fields if missing.
                    * format_id  A short description of the format
                                 ("mp4_h264_opus" or "19").
                                Technically optional, but strongly recommended.
                    * format_note Additional info about the format
                                 ("3D" or "DASH video")
                    * width      Width of the video, if known
                    * height     Height of the video, if known
                    * resolution Textual description of width and height
                    * tbr        Average bitrate of audio and video in KBit/s
                    * abr        Average audio bitrate in KBit/s
                    * acodec     Name of the audio codec in use
                    * asr        Audio sampling rate in Hertz
                    * vbr        Average video bitrate in KBit/s
                    * fps        Frame rate
                    * vcodec     Name of the video codec in use
                    * container  Name of the container format
                    * filesize   The number of bytes, if known in advance
                    * filesize_approx  An estimate for the number of bytes
                    * player_url SWF Player URL (used for rtmpdump).
                    * protocol   The protocol that will be used for the actual
                                 download, lower-case.
                                 "http", "https", "rtsp", "rtmp", "rtmpe",
                                 "m3u8", "m3u8_native" or "http_dash_segments".
                    * fragment_base_url
                                 Base URL for fragments. Each fragment's path
                                 value (if present) will be relative to
                                 this URL.
                    * fragments  A list of fragments of a fragmented media.
                                 Each fragment entry must contain either an url
                                 or a path. If an url is present it should be
                                 considered by a client. Otherwise both path and
                                 fragment_base_url must be present. Here is
                                 the list of all potential fields:
                                 * "url" - fragment's URL
                                 * "path" - fragment's path relative to
                                            fragment_base_url
                                 * "duration" (optional, int or float)
                                 * "filesize" (optional, int)
                    * preference Order number of this format. If this field is
                                 present and not None, the formats get sorted
                                 by this field, regardless of all other values.
                                 -1 for default (order by other properties),
                                 -2 or smaller for less than default.
                                 < -1000 to hide the format (if there is
                                    another one which is strictly better)
                    * language   Language code, e.g. "de" or "en-US".
                    * language_preference  Is this in the language mentioned in
                                 the URL?
                                 10 if it's what the URL is about,
                                 -1 for default (don't know),
                                 -10 otherwise, other values reserved for now.
                    * quality    Order number of the video quality of this
                                 format, irrespective of the file format.
                                 -1 for default (order by other properties),
                                 -2 or smaller for less than default.
                    * source_preference  Order number for this video source
                                  (quality takes higher priority)
                                 -1 for default (order by other properties),
                                 -2 or smaller for less than default.
                    * http_headers  A dictionary of additional HTTP headers
                                 to add to the request.
                    * stretched_ratio  If given and not 1, indicates that the
                                 video's pixels are not square.
                                 width : height ratio as float.
                    * no_resume  The server does not support resuming the
                                 (HTTP or RTMP) download. Boolean.
                    * downloader_options  A dictionary of downloader options as
                                 described in FileDownloader
    url:            Final video URL.
    ext:            Video filename extension.
    format:         The video format, defaults to ext (used for --get-format)
    player_url:     SWF Player URL (used for rtmpdump).
    The following fields are optional:
    alt_title:      A secondary title of the video.
    display_id      An alternative identifier for the video, not necessarily
                    unique, but available before title. Typically, id is
                    something like "4234987", title "Dancing naked mole rats",
                    and display_id "dancing-naked-mole-rats"
    thumbnails:     A list of dictionaries, with the following entries:
                        * "id" (optional, string) - Thumbnail format ID
                        * "url"
                        * "preference" (optional, int) - quality of the image
                        * "width" (optional, int)
                        * "height" (optional, int)
                        * "resolution" (optional, string "{width}x{height}",
                                        deprecated)
                        * "filesize" (optional, int)
    thumbnail:      Full URL to a video thumbnail image.
    description:    Full video description.
    uploader:       Full name of the video uploader.
    license:        License name the video is licensed under.
    creator:        The creator of the video.
    release_date:   The date (YYYYMMDD) when the video was released.
    timestamp:      UNIX timestamp of the moment the video became available.
    upload_date:    Video upload date (YYYYMMDD).
                    If not explicitly set, calculated from timestamp.
    uploader_id:    Nickname or id of the video uploader.
    uploader_url:   Full URL to a personal webpage of the video uploader.
    channel:        Full name of the channel the video is uploaded on.
                    Note that channel fields may or may not repeat uploader
                    fields. This depends on a particular extractor.
    channel_id:     Id of the channel.
    channel_url:    Full URL to a channel webpage.
    location:       Physical location where the video was filmed.
    subtitles:      The available subtitles as a dictionary in the format
                    {tag: subformats}. "tag" is usually a language code, and
                    "subformats" is a list sorted from lower to higher
                    preference, each element is a dictionary with the "ext"
                    entry and one of:
                        * "data": The subtitles file contents
                        * "url": A URL pointing to the subtitles file
                    "ext" will be calculated from URL if missing
    automatic_captions: Like 'subtitles', used by the YoutubeIE for
                    automatically generated captions
    duration:       Length of the video in seconds, as an integer or float.
    view_count:     How many users have watched the video on the platform.
    like_count:     Number of positive ratings of the video
    dislike_count:  Number of negative ratings of the video
    repost_count:   Number of reposts of the video
    average_rating: Average rating give by users, the scale used depends on the webpage
    comment_count:  Number of comments on the video
    comments:       A list of comments, each with one or more of the following
                    properties (all but one of text or html optional):
                        * "author" - human-readable name of the comment author
                        * "author_id" - user ID of the comment author
                        * "id" - Comment ID
                        * "html" - Comment as HTML
                        * "text" - Plain text of the comment
                        * "timestamp" - UNIX timestamp of comment
                        * "parent" - ID of the comment this one is replying to.
                                     Set to "root" to indicate that this is a
                                     comment to the original video.
    age_limit:      Age restriction for the video, as an integer (years)
    webpage_url:    The URL to the video webpage, if given to youtube-dl it
                    should allow to get the same result again. (It will be set
                    by YoutubeDL if it's missing)
    categories:     A list of categories that the video falls in, for example
                    ["Sports", "Berlin"]
    tags:           A list of tags assigned to the video, e.g. ["sweden", "pop music"]
    is_live:        True, False, or None (=unknown). Whether this video is a
                    live stream that goes on instead of a fixed-length video.
    start_time:     Time in seconds where the reproduction should start, as
                    specified in the URL.
    end_time:       Time in seconds where the reproduction should end, as
                    specified in the URL.
    chapters:       A list of dictionaries, with the following entries:
                        * "start_time" - The start time of the chapter in seconds
                        * "end_time" - The end time of the chapter in seconds
                        * "title" (optional, string)
    The following fields should only be used when the video belongs to some logical
    chapter or section:
    chapter:        Name or title of the chapter the video belongs to.
    chapter_number: Number of the chapter the video belongs to, as an integer.
    chapter_id:     Id of the chapter the video belongs to, as a unicode string.
    The following fields should only be used when the video is an episode of some
    series, programme or podcast:
    series:         Title of the series or programme the video episode belongs to.
    season:         Title of the season the video episode belongs to.
    season_number:  Number of the season the video episode belongs to, as an integer.
    season_id:      Id of the season the video episode belongs to, as a unicode string.
    episode:        Title of the video episode. Unlike mandatory video title field,
                    this field should denote the exact title of the video episode
                    without any kind of decoration.
    episode_number: Number of the video episode within a season, as an integer.
    episode_id:     Id of the video episode, as a unicode string.
    The following fields should only be used when the media is a track or a part of
    a music album:
    track:          Title of the track.
    track_number:   Number of the track within an album or a disc, as an integer.
    track_id:       Id of the track (useful in case of custom indexing, e.g. 6.iii),
                    as a unicode string.
    artist:         Artist(s) of the track.
    genre:          Genre(s) of the track.
    album:          Title of the album the track belongs to.
    album_type:     Type of the album (e.g. "Demo", "Full-length", "Split", "Compilation", etc).
    album_artist:   List of all artists appeared on the album (e.g.
                    "Ash Borer / Fell Voices" or "Various Artists", useful for splits
                    and compilations).
    disc_number:    Number of the disc or other physical medium the track belongs to,
                    as an integer.
    release_year:   Year (YYYY) when the album was released.
    Unless mentioned otherwise, the fields should be Unicode strings.
    Unless mentioned otherwise, None is equivalent to absence of information.
    _type "playlist" indicates multiple videos.
    There must be a key "entries", which is a list, an iterable, or a PagedList
    object, each element of which is a valid dictionary by this specification.
    Additionally, playlists can have "id", "title", "description", "uploader",
    "uploader_id", "uploader_url" attributes with the same semantics as videos
    (see above).
    _type "multi_video" indicates that there are multiple videos that
    form a single show, for examples multiple acts of an opera or TV episode.
    It must have an entries key like a playlist and contain all the keys
    required for a video at the same time.
    _type "url" indicates that the video must be extracted from another
    location, possibly by a different extractor. Its only required key is:
    "url" - the next URL to extract.
    The key "ie_key" can be set to the class name (minus the trailing "IE",
    e.g. "Youtube") if the extractor class is known in advance.
    Additionally, the dictionary may have any properties of the resolved entity
    known in advance, for example "title" if the title of the referred video is
    known ahead of time.
    _type "url_transparent" entities have the same specification as "url", but
    indicate that the given additional information is more precise than the one
    associated with the resolved URL.
    This is useful when a site employs a video service that hosts the video and
    its technical metadata, but that video service does not embed a useful
    title, description etc.
    Subclasses of this one should re-define the _real_initialize() and
    _real_extract() methods and define a _VALID_URL regexp.
    Probably, they should also be added to the list of extractors.
    _GEO_BYPASS attribute may be set to False in order to disable
    geo restriction bypass mechanisms for a particular extractor.
    Though it won't disable explicit geo restriction bypass based on
    country code provided with geo_bypass_country.
    _GEO_COUNTRIES attribute may contain a list of presumably geo unrestricted
    countries for this extractor. One of these countries will be used by
    geo restriction bypass mechanism right away in order to bypass
    geo restriction, of course, if the mechanism is not disabled.
    _GEO_IP_BLOCKS attribute may contain a list of presumably geo unrestricted
    IP blocks in CIDR notation for this extractor. One of these IP blocks
    will be used by geo restriction bypass mechanism similarly
    to _GEO_COUNTRIES.
    Finally, the _WORKING attribute should be set to False for broken IEs
    in order to warn the users and skip the tests.
    """

    _ready = False
    _downloader = None
    _x_forwarded_for_ip = None
    _GEO_BYPASS = True
    _GEO_COUNTRIES = None
    _GEO_IP_BLOCKS = None
    _WORKING = True

    def __init__(self, downloader=None):
        """Constructor. Receives an optional downloader."""
        self._ready = False
        self._x_forwarded_for_ip = None
        self.set_downloader(downloader)

    @classmethod
    def suitable(cls, url):
        """Receives a URL and returns True if suitable for this IE."""

        # This does not use has/getattr intentionally - we want to know whether
        # we have cached the regexp for *this* class, whereas getattr would also
        # match the superclass
        if '_VALID_URL_RE' not in cls.__dict__:
            cls._VALID_URL_RE = re.compile(cls._VALID_URL)
        return cls._VALID_URL_RE.match(url) is not None

    @classmethod
    def _match_id(cls, url):
        if '_VALID_URL_RE' not in cls.__dict__:
            cls._VALID_URL_RE = re.compile(cls._VALID_URL)
        m = cls._VALID_URL_RE.match(url)
        assert m
        return compat_str(m.group('id'))
 @classmethod
    def _match_id(cls, url):
        if '_VALID_URL_RE' not in cls.__dict__:
            cls._VALID_URL_RE = re.compile(cls._VALID_URL)
        m = cls._VALID_URL_RE.match(url)
        assert m
        return compat_str(m.group('id'))

    @classmethod
    def working(cls):
        """Getter method for _WORKING."""
        return cls._WORKING

    def initialize(self):
        """Initializes an instance (authentication, etc)."""
        self._initialize_geo_bypass({
            'countries': self._GEO_COUNTRIES,
            'ip_blocks': self._GEO_IP_BLOCKS,
        })
        if not self._ready:
            self._real_initialize()
            self._ready = True

    def _initialize_geo_bypass(self, geo_bypass_context):
        """
        Initialize geo restriction bypass mechanism.
        This method is used to initialize geo bypass mechanism based on faking
        X-Forwarded-For HTTP header. A random country from provided country list
        is selected and a random IP belonging to this country is generated. This
        IP will be passed as X-Forwarded-For HTTP header in all subsequent
        HTTP requests.
        This method will be used for initial geo bypass mechanism initialization
        during the instance initialization with _GEO_COUNTRIES and
        _GEO_IP_BLOCKS.
        You may also manually call it from extractor's code if geo bypass
        information is not available beforehand (e.g. obtained during
        extraction) or due to some other reason. In this case you should pass
        this information in geo bypass context passed as first argument. It may
        contain following fields:
        countries:  List of geo unrestricted countries (similar
                    to _GEO_COUNTRIES)
        ip_blocks:  List of geo unrestricted IP blocks in CIDR notation
                    (similar to _GEO_IP_BLOCKS)
        """
        if not self._x_forwarded_for_ip:

            # Geo bypass mechanism is explicitly disabled by user
            if not self._downloader.params.get('geo_bypass', True):
                return

            if not geo_bypass_context:
                geo_bypass_context = {}

            # Backward compatibility: previously _initialize_geo_bypass
            # expected a list of countries, some 3rd party code may still use
            # it this way
            if isinstance(geo_bypass_context, (list, tuple)):
                geo_bypass_context = {
                    'countries': geo_bypass_context,
                }

            # The whole point of geo bypass mechanism is to fake IP
            # as X-Forwarded-For HTTP header based on some IP block or
            # country code.

            # Path 1: bypassing based on IP block in CIDR notation

            # Explicit IP block specified by user, use it right away
            # regardless of whether extractor is geo bypassable or not
            ip_block = self._downloader.params.get('geo_bypass_ip_block', None)

            # Otherwise use random IP block from geo bypass context but only
            # if extractor is known as geo bypassable
            if not ip_block:
                ip_blocks = geo_bypass_context.get('ip_blocks')
                if self._GEO_BYPASS and ip_blocks:
                    ip_block = random.choice(ip_blocks)

            if ip_block:
                self._x_forwarded_for_ip = GeoUtils.random_ipv4(ip_block)
                if self._downloader.params.get('verbose', False):
                    self._downloader.to_screen(
                        '[debug] Using fake IP %s as X-Forwarded-For.'
                        % self._x_forwarded_for_ip)
                return

            # Path 2: bypassing based on country code

            # Explicit country code specified by user, use it right away
            # regardless of whether extractor is geo bypassable or not
            country = self._downloader.params.get('geo_bypass_country', None)

            # Otherwise use random country code from geo bypass context but
            # only if extractor is known as geo bypassable
            if not country:
                countries = geo_bypass_context.get('countries')
                if self._GEO_BYPASS and countries:
                    country = random.choice(countries)

            if country:
                self._x_forwarded_for_ip = GeoUtils.random_ipv4(country)
                if self._downloader.params.get('verbose', False):
                    self._downloader.to_screen(
                        '[debug] Using fake IP %s (%s) as X-Forwarded-For.'
                        % (self._x_forwarded_for_ip, country.upper()))

    def extract(self, url):
        """Extracts URL information and returns it in list of dicts."""
        try:
            for _ in range(2):
                try:
                    self.initialize()
                    ie_result = self._real_extract(url)
                    if self._x_forwarded_for_ip:
                        ie_result['__x_forwarded_for_ip'] = self._x_forwarded_for_ip
                    return ie_result
                except GeoRestrictedError as e:
                    if self.__maybe_fake_ip_and_retry(e.countries):
                        continue
                    raise
        except ExtractorError:
            raise
        except compat_http_client.IncompleteRead as e:
            raise ExtractorError('A network error has occurred.', cause=e, expected=True)
        except (KeyError, StopIteration) as e:
            raise ExtractorError('An extractor error has occurred.', cause=e)

    def __maybe_fake_ip_and_retry(self, countries):
        if (not self._downloader.params.get('geo_bypass_country', None)
                and self._GEO_BYPASS
                and self._downloader.params.get('geo_bypass', True)
                and not self._x_forwarded_for_ip
                and countries):
            country_code = random.choice(countries)
            self._x_forwarded_for_ip = GeoUtils.random_ipv4(country_code)
            if self._x_forwarded_for_ip:
                self.report_warning(
                    'Video is geo restricted. Retrying extraction with fake IP %s (%s) as X-Forwarded-For.'
                    % (self._x_forwarded_for_ip, country_code.upper()))
                return True
        return False
def set_downloader(self, downloader):
        """Sets the downloader for this IE."""
        self._downloader = downloader

    def _real_initialize(self):
        """Real initialization process. Redefine in subclasses."""
        pass

    def _real_extract(self, url):
        """Real extraction process. Redefine in subclasses."""
        pass

    @classmethod
    def ie_key(cls):
        """A string for getting the InfoExtractor with get_info_extractor"""
        return compat_str(cls.__name__[:-2])

    @property
    def IE_NAME(self):
        return compat_str(type(self).__name__[:-2])

    @staticmethod
    def __can_accept_status_code(err, expected_status):
        assert isinstance(err, compat_urllib_error.HTTPError)
        if expected_status is None:
            return False
        if isinstance(expected_status, compat_integer_types):
            return err.code == expected_status
        elif isinstance(expected_status, (list, tuple)):
            return err.code in expected_status
        elif callable(expected_status):
            return expected_status(err.code) is True
        else:
            assert False

    def _request_webpage(self, url_or_request, video_id, note=None, errnote=None, fatal=True, data=None, headers={}, query={}, expected_status=None):
        """
        Return the response handle.
        See _download_webpage docstring for arguments specification.
        """
        if note is None:
            self.report_download_webpage(video_id)
        elif note is not False:
            if video_id is None:
                self.to_screen('%s' % (note,))
            else:
                self.to_screen('%s: %s' % (video_id, note))

        # Some sites check X-Forwarded-For HTTP header in order to figure out
        # the origin of the client behind proxy. This allows bypassing geo
        # restriction by faking this header's value to IP that belongs to some
        # geo unrestricted country. We will do so once we encounter any
        # geo restriction error.
        if self._x_forwarded_for_ip:
            if 'X-Forwarded-For' not in headers:
                headers['X-Forwarded-For'] = self._x_forwarded_for_ip

        if isinstance(url_or_request, compat_urllib_request.Request):
            url_or_request = update_Request(
                url_or_request, data=data, headers=headers, query=query)
        else:
            if query:
                url_or_request = update_url_query(url_or_request, query)
            if data is not None or headers:
                url_or_request = sanitized_Request(url_or_request, data, headers)
        exceptions = [compat_urllib_error.URLError, compat_http_client.HTTPException, socket.error]
        if hasattr(ssl, 'CertificateError'):
            exceptions.append(ssl.CertificateError)
        try:
            return self._downloader.urlopen(url_or_request)
        except tuple(exceptions) as err:
            if isinstance(err, compat_urllib_error.HTTPError):
                if self.__can_accept_status_code(err, expected_status):
                    # Retain reference to error to prevent file object from
                    # being closed before it can be read. Works around the
                    # effects of <https://bugs.python.org/issue15002>
                    # introduced in Python 3.4.1.
                    err.fp._error = err
                    return err.fp

            if errnote is False:
                return False
            if errnote is None:
                errnote = 'Unable to download webpage'

            errmsg = '%s: %s' % (errnote, error_to_compat_str(err))
            if fatal:
                raise ExtractorError(errmsg, sys.exc_info()[2], cause=err)
            else:
                self._downloader.report_warning(errmsg)
                return False

    def _download_webpage_handle(self, url_or_request, video_id, note=None, errnote=None, fatal=True, encoding=None, data=None, headers={}, query={}, expected_status=None):
        """
        Return a tuple (page content as string, URL handle).
        See _download_webpage docstring for arguments specification.
        """
        # Strip hashes from the URL (#1038)
        if isinstance(url_or_request, (compat_str, str)):
            url_or_request = url_or_request.partition('#')[0]

        urlh = self._request_webpage(url_or_request, video_id, note, errnote, fatal, data=data, headers=headers, query=query, expected_status=expected_status)
        if urlh is False:
            assert not fatal
            return False
        content = self._webpage_read_content(urlh, url_or_request, video_id, note, errnote, fatal, encoding=encoding)
        return (content, urlh)
def _download_webpage(
            self, url_or_request, video_id, note=None, errnote=None,
            fatal=True, tries=1, timeout=5, encoding=None, data=None,
            headers={}, query={}, expected_status=None):
        """
        Return the data of the page as a string.
        Arguments:
        url_or_request -- plain text URL as a string or
            a compat_urllib_request.Requestobject
        video_id -- Video/playlist/item identifier (string)
        Keyword arguments:
        note -- note printed before downloading (string)
        errnote -- note printed in case of an error (string)
        fatal -- flag denoting whether error should be considered fatal,
            i.e. whether it should cause ExtractionError to be raised,
            otherwise a warning will be reported and extraction continued
        tries -- number of tries
        timeout -- sleep interval between tries
        encoding -- encoding for a page content decoding, guessed automatically
            when not explicitly specified
        data -- POST data (bytes)
        headers -- HTTP headers (dict)
        query -- URL query (dict)
        expected_status -- allows to accept failed HTTP requests (non 2xx
            status code) by explicitly specifying a set of accepted status
            codes. Can be any of the following entities:
                - an integer type specifying an exact failed status code to
                  accept
                - a list or a tuple of integer types specifying a list of
                  failed status codes to accept
                - a callable accepting an actual failed status code and
                  returning True if it should be accepted
            Note that this argument does not affect success status codes (2xx)
            which are always accepted.
        """

        success = False
        try_count = 0
        while success is False:
            try:
                res = self._download_webpage_handle(
                    url_or_request, video_id, note, errnote, fatal,
                    encoding=encoding, data=data, headers=headers, query=query,
                    expected_status=expected_status)
                success = True
            except compat_http_client.IncompleteRead as e:
                try_count += 1
                if try_count >= tries:
                    raise e
                self._sleep(timeout, video_id)
        if res is False:
            return res
        else:
            content, _ = res
            return content

    def _download_xml_handle(
            self, url_or_request, video_id, note='Downloading XML',
            errnote='Unable to download XML', transform_source=None,
            fatal=True, encoding=None, data=None, headers={}, query={},
            expected_status=None):
        """
        Return a tuple (xml as an compat_etree_Element, URL handle).
        See _download_webpage docstring for arguments specification.
        """
        res = self._download_webpage_handle(
            url_or_request, video_id, note, errnote, fatal=fatal,
            encoding=encoding, data=data, headers=headers, query=query,
            expected_status=expected_status)
        if res is False:
            return res
        xml_string, urlh = res
        return self._parse_xml(
            xml_string, video_id, transform_source=transform_source,
            fatal=fatal), urlh
