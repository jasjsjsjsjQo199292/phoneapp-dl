
from __future__ import unicode_literals

__license__ = 'Public Domain'

import codecs
import io
import os
import random
import sys


from .options import (
    parseOpts,
)
from .compat import (
    compat_getpass,
    compat_shlex_split,
    workaround_optparse_bug9161,
)
from .utils import (
    DateRange,
    decodeOption,
    DEFAULT_OUTTMPL,
    DownloadError,
    expand_path,
    match_filter_func,
    MaxDownloadsReached,
    preferredencoding,
    read_batch_urls,
    SameFileError,
    setproctitle,
    std_headers,
    write_string,
    render_table,
)
from .update import update_self
from .downloader import (
    FileDownloader,
)
from .extractor import gen_extractors, list_extractors
from .extractor.adobepass import MSO_INFO
from .YoutubeDL import YoutubeDL


def _real_main(argv=None):
    # Compatibility fixes for Windows
    if sys.platform == 'win32':
        # https://github.com/ytdl-org/youtube-dl/issues/820
        codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

    workaround_optparse_bug9161()

    setproctitle('youtube-dl')

    parser, opts, args = parseOpts(argv)

    # Set user agent
    if opts.user_agent is not None:
        std_headers['User-Agent'] = opts.user_agent

    # Set referer
    if opts.referer is not None:
        std_headers['Referer'] = opts.referer

    # Custom HTTP headers
    if opts.headers is not None:
        for h in opts.headers:
            if ':' not in h:
                parser.error('wrong header formatting, it should be key:value, not "%s"' % h)
            key, value = h.split(':', 1)
            if opts.verbose:
                write_string('[debug] Adding header from command line option %s:%s\n' % (key, value))
            std_headers[key] = value

    # Dump user agent
    if opts.dump_user_agent:
        write_string(std_headers['User-Agent'] + '\n', out=sys.stdout)
        sys.exit(0)

    # Batch file verification
    batch_urls = []
    if opts.batchfile is not None:
        try:
            if opts.batchfile == '-':
                batchfd = sys.stdin
            else:
                batchfd = io.open(
                    expand_path(opts.batchfile),
                    'r', encoding='utf-8', errors='ignore')
            batch_urls = read_batch_urls(batchfd)
            if opts.verbose:
                write_string('[debug] Batch file urls: ' + repr(batch_urls) + '\n')
        except IOError:
            sys.exit('ERROR: batch file %s could not be read' % opts.batchfile)
    all_urls = batch_urls + [url.strip() for url in args]  # batch_urls are already striped in read_batch_urls
    _enc = preferredencoding()
    all_urls = [url.decode(_enc, 'ignore') if isinstance(url, bytes) else url for url in all_urls]

    if opts.list_extractors:
        for ie in list_extractors(opts.age_limit):
            write_string(ie.IE_NAME + (' (CURRENTLY BROKEN)' if not ie._WORKING else '') + '\n', out=sys.stdout)
            matchedUrls = [url for url in all_urls if ie.suitable(url)]
            for mu in matchedUrls:
                write_string('  ' + mu + '\n', out=sys.stdout)
        sys.exit(0)
    if opts.list_extractor_descriptions:
        for ie in list_extractors(opts.age_limit):
            if not ie._WORKING:
                continue
            desc = getattr(ie, 'IE_DESC', ie.IE_NAME)
            if desc is False:
                continue
            if hasattr(ie, 'SEARCH_KEY'):
                _SEARCHES = ('cute kittens', 'slithering pythons', 'falling cat', 'angry poodle', 'purple fish', 'running tortoise', 'sleeping bunny', 'burping cow')
                _COUNTS = ('', '5', '10', 'all')
                desc += ' (Example: "%s%s:%s" )' % (ie.SEARCH_KEY, random.choice(_COUNTS), random.choice(_SEARCHES))
            write_string(desc + '\n', out=sys.stdout)
        sys.exit(0)
    if opts.ap_list_mso:
        table = [[mso_id, mso_info['name']] for mso_id, mso_info in MSO_INFO.items()]
        write_string('Supported TV Providers:\n' + render_table(['mso', 'mso name'], table) + '\n', out=sys.stdout)
        sys.exit(0)

    # Conflicting, missing and erroneous options
    if opts.usenetrc and (opts.username is not None or opts.password is not None):
        parser.error('using .netrc conflicts with giving username/password')
    if opts.password is not None and opts.username is None:
        parser.error('account username missing\n')
    if opts.ap_password is not None and opts.ap_username is None:
        parser.error('TV Provider account username missing\n')
    if opts.outtmpl is not None and (opts.usetitle or opts.autonumber or opts.useid):
        parser.error('using output template conflicts with using title, video ID or auto number')
    if opts.autonumber_size is not None:
        if opts.autonumber_size <= 0:
            parser.error('auto number size must be positive')
    if opts.autonumber_start is not None:
        if opts.autonumber_start < 0:
            parser.error('auto number start must be positive or 0')
    if opts.usetitle and opts.useid:
        parser.error('using title conflicts with using video ID')
    if opts.username is not None and opts.password is None:
        opts.password = compat_getpass('Type account password and press [Return]: ')
    if opts.ap_username is not None and opts.ap_password is None:
        opts.ap_password = compat_getpass('Type TV provider account password and press [Return]: ')
    if opts.ratelimit is not None:
        numeric_limit = FileDownloader.parse_bytes(opts.ratelimit)
        if numeric_limit is None:
            parser.error('invalid rate limit specified')
        opts.ratelimit = numeric_limit
    if opts.min_filesize is not None:
        numeric_limit = FileDownloader.parse_bytes(opts.min_filesize)
        if numeric_limit is None:
            parser.error('invalid min_filesize specified')
        opts.min_filesize = numeric_limit
    if opts.max_filesize is not None:
        numeric_limit = FileDownloader.parse_bytes(opts.max_filesize)
        if numeric_limit is None:
            parser.error('invalid max_filesize specified')
        opts.max_filesize = numeric_limit
    if opts.sleep_interval is not None:
        if opts.sleep_interval < 0:
            parser.error('sleep interval must be positive or 0')
    if opts.max_sleep_interval is not None:
        if opts.max_sleep_interval < 0:
            parser.error('max sleep interval must be positive or 0')
        if opts.sleep_interval is None:
            parser.error('min sleep interval must be specified, use --min-sleep-interval')
        if opts.max_sleep_interval < opts.sleep_interval:
            parser.error('max sleep interval must be greater than or equal to min sleep interval')
    else:
        opts.max_sleep_interval = opts.sleep_interval
    if opts.ap_mso and opts.ap_mso not in MSO_INFO:
        parser.error('Unsupported TV Provider, use --ap-list-mso to get a list of supported TV Providers')

    def parse_retries(retries):
        if retries in ('inf', 'infinite'):
            parsed_retries = float('inf')
        else:
            try:
                parsed_retries = int(retries)
            except (TypeError, ValueError):
                parser.error('invalid retry count specified')
        return parsed_retries
    if opts.retries is not None:
        opts.retries = parse_retries(opts.retries)
    if opts.fragment_retries is not None:
        opts.fragment_retries = parse_retries(opts.fragment_retries)
    if opts.buffersize is not None:
        numeric_buffersize = FileDownloader.parse_bytes(opts.buffersize)
        if numeric_buffersize is None:
            parser.error('invalid buffer size specified')
        opts.buffersize = numeric_buffersize
    if opts.http_chunk_size is not None:
        numeric_chunksize = FileDownloader.parse_bytes(opts.http_chunk_size)
        if not numeric_chunksize:
            parser.error('invalid http chunk size specified')
        opts.http_chunk_size = numeric_chunksize
    if opts.playliststart <= 0:
        raise ValueError('Playlist start must be positive')
    if opts.playlistend not in (-1, None) and opts.playlistend < opts.playliststart:
        raise ValueError('Playlist end must be greater than playlist start')
    if opts.extractaudio:
        if opts.audioformat not in ['best', 'aac', 'flac', 'mp3', 'm4a', 'opus', 'vorbis', 'wav']:
            parser.error('invalid audio format specified')
    if opts.audioquality:
        opts.audioquality = opts.audioquality.strip('k').strip('K')
        if not opts.audioquality.isdigit():
            parser.error('invalid audio quality specified')
    if opts.recodevideo is not None:
        if opts.recodevideo not in ['mp4', 'flv', 'webm', 'ogg', 'mkv', 'avi']:
            parser.error('invalid video recode format specified')
    if opts.convertsubtitles is not None:
        if opts.convertsubtitles not in ['srt', 'vtt', 'ass', 'lrc']:
            parser.error('invalid subtitle format specified')

    if opts.date is not None:
        date = DateRange.day(opts.date)
    else:
        date = DateRange(opts.dateafter, opts.datebefore)

    # Do not download videos when there are audio-only formats
    if opts.extractaudio and not opts.keepvideo and opts.format is None:
        opts.format = 'bestaudio/best'

    # --all-sub automatically sets --write-sub if --write-auto-sub is not given
    # this was the old behaviour if only --all-sub was given.
    if opts.allsubtitles and not opts.writeautomaticsub:
        opts.writesubtitles = True
