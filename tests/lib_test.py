import contextlib
import json
import zipfile

import pytest
import responses
from requests.exceptions import ConnectionError
from ugoira.lib import (PixivError, download_zip, is_ugoira, login, make_gif,
                        save_zip)
from wand.image import Image


def test_login_miss_id():
    """Test :func:`ugoira.lib.login` try, but missing id and raise
    :exception:`ugoira.lib.PixivError`.

    """

    id = None
    password = None
    with pytest.raises(PixivError):
        login(id, password)

    password = 'password'
    with pytest.raises(PixivError):
        login(id, password)


def test_login_miss_password():
    """Test :func:`ugoira.lib.login` try, but missing password and raise
    :exception:`ugoira.lib.PixivError`.

    """

    id = None
    password = None
    with pytest.raises(PixivError):
        login(id, password)

    id = 'item4'
    with pytest.raises(PixivError):
        login(id, password)


def test_login_pixiv_down(fx_valid_id_pw):
    """Test :func:`ugoira.lib.login` try, but pixiv down and raise
    :exception:`ugoira.lib.PixivError`.

    """

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'https://accounts.pixiv.net/login',
            'body': 'dead',
            'status': 404,
        })

        with pytest.raises(PixivError):
            login(*fx_valid_id_pw)

    test()


def test_login_pixiv_login_server_down(fx_valid_id_pw, fx_login_page_body):
    """Test :func:`ugoira.lib.login` try, but pixiv login server down and
    raise :exception:`ugoira.lib.PixivError`.

    """

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'https://accounts.pixiv.net/login',
            'body': fx_login_page_body,
            'status': 200,
        })
        responses.add(**{
            'method': responses.POST,
            'url': 'https://accounts.pixiv.net/api/login',
            'body': json.dumps({}),
            'content_type': 'application/json; charset=utf-8',
            'status': 404,
        })

        with pytest.raises(PixivError):
            login(*fx_valid_id_pw)

    test()


def test_login_pixiv_error(fx_valid_id_pw):
    """Test :func:`ugoira.lib.login` try, but pixiv error and raise
    :exception:`ugoira.lib.PixivError`.

    """

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'https://accounts.pixiv.net/login?lang=ja',
            'body': ConnectionError(json.dumps({})),
            'status': 500,
        })

        with pytest.raises(PixivError):
            login(*fx_valid_id_pw)

    test()


def test_login_pixiv_login_server_error(fx_valid_id_pw, fx_login_page_body):
    """Test :func:`ugoira.lib.login` try, but pixiv login server error and
    raise :exception:`ugoira.lib.PixivError`.

    """

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'https://accounts.pixiv.net/login',
            'body': fx_login_page_body,
            'status': 200,
        })
        responses.add(**{
            'method': responses.POST,
            'url': 'https://accounts.pixiv.net/api/login',
            'body': ConnectionError(json.dumps({})),
            'status': 500,
        })

        with pytest.raises(PixivError):
            login(*fx_valid_id_pw)

    test()


def test_login_valid(fx_valid_id_pw, fx_login_page_body):
    """Test :func:`ugoira.lib.login` successfully."""

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'https://accounts.pixiv.net/login',
            'body': fx_login_page_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
        })
        responses.add(**{
            'method': responses.POST,
            'url': 'https://accounts.pixiv.net/api/login',
            'body': json.dumps({
                'error': False,
                'message': '',
                'body': {
                    'success': {'redirect_to': 'http://www.pixiv.net/'},
                },
            }),
            'content_type': 'application/json; charset=utf-8',
            'status': 200,
        })

        try:
            login(*fx_valid_id_pw)
        except:
            raise AssertionError

    test()


def test_login_pw_is_too_short(fx_too_short_id_pw, fx_login_page_body):
    """Test :func:`ugoira.lib.login` with too short password.

    It must raise :class:`ugoira.lib.PixivError`.

    """

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'https://accounts.pixiv.net/login',
            'body': fx_login_page_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
        })
        with pytest.raises(PixivError):
            login(*fx_too_short_id_pw)

    test()


def test_login_pw_is_too_long(fx_too_long_id_pw, fx_login_page_body):
    """Test :func:`ugoira.lib.login` with too long password.

    It must raise :class:`ugoira.lib.PixivError`.

    """

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'https://accounts.pixiv.net/login',
            'body': fx_login_page_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
        })
        with pytest.raises(PixivError):
            login(*fx_too_long_id_pw)

    test()


def test_login_invalid(fx_invalid_id_pw, fx_login_page_body):
    """Test :func:`ugoira.lib.login` with invalid id/pw pair.

    It must raise :class:`ugoira.lib.PixivError`.

    """

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'https://accounts.pixiv.net/login',
            'body': fx_login_page_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
        })
        responses.add(**{
            'method': responses.POST,
            'url': 'https://accounts.pixiv.net/api/login',
            'body': json.dumps({
                'error': False,
                'message': '',
                'body': {
                    'validation_errors': {
                        'pixiv_id': ('Please check if your pixiv ID or'
                                     ' email address was entered correctly.'),
                    },
                },
            }),
            'content_type': 'application/json; charset=utf-8',
            'status': 200,
        })
        with pytest.raises(PixivError):
            login(*fx_invalid_id_pw)

    test()


def test_is_ugoira_true(fx_ugoira_body):
    """Test :func:`ugoira.lib.ugoira`.

    Result is :const:`True`.

    """

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'http://www.pixiv.net/member_illust.php'
                   '?mode=medium&illust_id=53239740',
            'body': fx_ugoira_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
            'match_querystring': True,
        })

        assert is_ugoira(53239740)

    test()


def test_is_ugoira_false(fx_non_ugoira_body):
    """Test :func:`ugoira.lib.ugoira`.

    Result is :const:`False`.

    """

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'http://www.pixiv.net/member_illust.php'
                   '?mode=medium&illust_id=53231212',
            'body': fx_non_ugoira_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
            'match_querystring': True,
        })

        assert not is_ugoira(53231212)

    test()


def test_download_zip_fail_head(fx_ugoira_body):
    """Test :func:`ugoira.lib.download_zip` with broken link.

    It must raise :class:`ugoira.lib.PixivError`.

    """

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'http://www.pixiv.net/member_illust.php'
                   '?mode=medium&illust_id=53239740',
            'body': fx_ugoira_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
            'match_querystring': True,
        })
        responses.add(**{
            'method': responses.HEAD,
            'url': 'http://i1.pixiv.net/img-zip-ugoira/img/'
                   '2015/10/27/22/10/14/53239740_ugoira600x600.zip',
            'status': 403,
        })

        with pytest.raises(PixivError):
            download_zip(53239740)

    test()


def test_download_zip_fail_get(fx_ugoira_body):
    """Test :func:`ugoira.lib.download_zip` with broken link.

    It must raise :class:`ugoira.lib.PixivError`.

    """

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'http://www.pixiv.net/member_illust.php'
                   '?mode=medium&illust_id=53239740',
            'body': fx_ugoira_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
            'match_querystring': True,
        })
        responses.add(**{
            'method': responses.HEAD,
            'url': 'http://i1.pixiv.net/img-zip-ugoira/img/'
                   '2015/10/27/22/10/14/53239740_ugoira600x600.zip',
            'status': 200,
        })
        responses.add(**{
            'method': responses.GET,
            'url': 'http://i1.pixiv.net/img-zip-ugoira/img/'
                   '2015/10/27/22/10/14/53239740_ugoira600x600.zip',
            'status': 403,
        })

        with pytest.raises(PixivError):
            download_zip(53239740)

    test()


def test_download_zip_success(fx_ugoira_body, fx_ugoira_zip):
    """Test :func:`ugoira.lib.download_zip` with correct link."""

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'http://www.pixiv.net/member_illust.php'
                   '?mode=medium&illust_id=53239740',
            'body': fx_ugoira_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
            'match_querystring': True,
        })
        responses.add(**{
            'method': responses.HEAD,
            'url': 'http://i1.pixiv.net/img-zip-ugoira/img/'
                   '2015/10/27/22/10/14/53239740_ugoira600x600.zip',
            'status': 200,
        })
        responses.add(**{
            'method': responses.GET,
            'url': 'http://i1.pixiv.net/img-zip-ugoira/img/'
                   '2015/10/27/22/10/14/53239740_ugoira600x600.zip',
            'body': fx_ugoira_zip,
            'content_type': 'application/zip',
            'status': 200,
        })

        data, frames = download_zip(53239740)
        assert data == fx_ugoira_zip

    test()


def test_make_gif(monkeypatch,
                  fx_tmpdir,
                  fx_ugoira_body,
                  fx_ugoira_zip,
                  fx_ugoira_frames):
    """Test :func:`ugoira.lib.make_gif` with correct link."""

    @contextlib.contextmanager
    def fake():
        yield str(fx_tmpdir)
    monkeypatch.setattr('tempfile.TemporaryDirectory', fake)

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'http://www.pixiv.net/member_illust.php'
                   '?mode=medium&illust_id=53239740',
            'body': fx_ugoira_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
            'match_querystring': True,
        })
        responses.add(**{
            'method': responses.HEAD,
            'url': 'http://i1.pixiv.net/img-zip-ugoira/img/'
                   '2015/10/27/22/10/14/53239740_ugoira600x600.zip',
            'status': 200,
        })
        responses.add(**{
            'method': responses.GET,
            'url': 'http://i1.pixiv.net/img-zip-ugoira/img/'
                   '2015/10/27/22/10/14/53239740_ugoira600x600.zip',
            'body': fx_ugoira_zip,
            'content_type': 'application/zip',
            'status': 200,
        })

        data, frames = download_zip(53239740)
        file = fx_tmpdir / 'test.gif'
        make_gif(str(file), data, fx_ugoira_frames)
        with Image(filename=str(file)) as img:
            assert img.format == 'GIF'
            assert len(img.sequence) == 3
            assert img.sequence[0].delay == 100
            assert img.sequence[1].delay == 200
            assert img.sequence[2].delay == 300

    test()


def test_make_gif_with_acceleration(monkeypatch,
                                    fx_tmpdir,
                                    fx_ugoira_body,
                                    fx_ugoira_zip,
                                    fx_ugoira_frames):
    """Test :func:`ugoira.lib.make_gif` with correct link and acceleration."""

    @contextlib.contextmanager
    def fake():
        yield str(fx_tmpdir)
    monkeypatch.setattr('tempfile.TemporaryDirectory', fake)

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'http://www.pixiv.net/member_illust.php'
                   '?mode=medium&illust_id=53239740',
            'body': fx_ugoira_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
            'match_querystring': True,
        })
        responses.add(**{
            'method': responses.HEAD,
            'url': 'http://i1.pixiv.net/img-zip-ugoira/img/'
                   '2015/10/27/22/10/14/53239740_ugoira600x600.zip',
            'status': 200,
        })
        responses.add(**{
            'method': responses.GET,
            'url': 'http://i1.pixiv.net/img-zip-ugoira/img/'
                   '2015/10/27/22/10/14/53239740_ugoira600x600.zip',
            'body': fx_ugoira_zip,
            'content_type': 'application/zip',
            'status': 200,
        })

        data, frames = download_zip(53239740)
        file = fx_tmpdir / 'test.gif'
        make_gif(str(file), data, fx_ugoira_frames, 10.0)
        with Image(filename=str(file)) as img:
            assert img.format == 'GIF'
            assert len(img.sequence) == 3
            assert img.sequence[0].delay == 10
            assert img.sequence[1].delay == 20
            assert img.sequence[2].delay == 30

    test()


def test_save_zip(monkeypatch,
                  fx_tmpdir,
                  fx_ugoira_body,
                  fx_ugoira_zip,
                  fx_ugoira_frames):
    """Test :func:`ugoira.lib.save_zip` with correct link."""

    @contextlib.contextmanager
    def fake():
        yield str(fx_tmpdir)
    monkeypatch.setattr('tempfile.TemporaryDirectory', fake)

    @responses.activate
    def test():
        responses.reset()
        responses.add(**{
            'method': responses.GET,
            'url': 'http://www.pixiv.net/member_illust.php'
                   '?mode=medium&illust_id=53239740',
            'body': fx_ugoira_body,
            'content_type': 'text/html; charset=utf-8',
            'status': 200,
            'match_querystring': True,
        })
        responses.add(**{
            'method': responses.HEAD,
            'url': 'http://i1.pixiv.net/img-zip-ugoira/img/'
                   '2015/10/27/22/10/14/53239740_ugoira600x600.zip',
            'status': 200,
        })
        responses.add(**{
            'method': responses.GET,
            'url': 'http://i1.pixiv.net/img-zip-ugoira/img/'
                   '2015/10/27/22/10/14/53239740_ugoira600x600.zip',
            'body': fx_ugoira_zip,
            'content_type': 'application/zip',
            'status': 200,
        })

        data, frames = download_zip(53239740)
        file = fx_tmpdir / 'test.zip'

        save_zip(str(file), data)

        with zipfile.ZipFile(str(file)) as f:
            namelist = f.namelist()
            assert len(namelist) == len(fx_ugoira_frames)

            for filename in fx_ugoira_frames.keys():
                assert filename in namelist

    test()
