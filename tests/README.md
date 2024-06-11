<!-- 23/05/2024 -->

Running ``pytest`` suite together might result in errors, while running individually they all passed. This is a well-known problem, and there is not a one-size-fits-all approach to address this problem.

This test suite suffers this problem. For the code revision tag ``v0.3.0``, when running all tests together, test method [def test_integration_valid_login(test_client):](https://github.com/behai-nguyen/fastapi_learning/blob/cb2a77e45475a360515c7d08c36ff59ab34f0cd1/tests/integration/test_auth_itgt.py#L26-L52) in module [integration/test_auth_itgt.py](https://github.com/behai-nguyen/fastapi_learning/blob/cb2a77e45475a360515c7d08c36ff59ab34f0cd1/tests/integration/test_auth_itgt.py) results in the following failure:

```python
...
        finally:
            # Logout. Clean up server sessions.
>           logout(login_response, test_client)
E           UnboundLocalError: local variable 'login_response' referenced before assignment
```

I can't address this problem. I settled for the work around in this [Stack Overflow answer](https://stackoverflow.com/a/71428106), basically reloading the ``main`` module on every test:

```python
def test_app():
    import main
    importlib.reload(main)  # reset module state
    # do something with main.app
```

Reloading the ``main`` module on every test results in an **ignored exception**:

```
Exception ignored in: <function AbstractConnection.__del__ at 0x7f9cab554670>
...
RuntimeError: Event loop is closed
```

🐍 But all tests passed.

Full ``pytest`` logs for code revision tag ``v0.3.0`` without and with reloading ``main`` module on every test are included in the following two sections.

## Without reloading the ``main`` Module on Every Test

For the code revision tag ``v0.3.0``, when running all tests together, test method [def test_integration_valid_login(test_client):](https://github.com/behai-nguyen/fastapi_learning/blob/cb2a77e45475a360515c7d08c36ff59ab34f0cd1/tests/integration/test_auth_itgt.py#L26-L52) in module [integration/test_auth_itgt.py](https://github.com/behai-nguyen/fastapi_learning/blob/cb2a77e45475a360515c7d08c36ff59ab34f0cd1/tests/integration/test_auth_itgt.py) results in the following failure:

```
(venv) behai@hp-pavilion-15:~/fastapi_learning$ venv/bin/pytest
================================================= test session starts ==================================================
platform linux -- Python 3.10.7, pytest-8.2.0, pluggy-1.5.0
rootdir: /home/behai/fastapi_learning
configfile: pytest.ini
plugins: anyio-4.3.0
collected 10 items

tests/integration/test_admin_itgt.py ..                                                                          [ 20%]
tests/integration/test_auth_itgt.py F.......                                                                     [100%]

======================================================= FAILURES =======================================================
_____________________________________________ test_integration_valid_login _____________________________________________
self = <redis.asyncio.connection.Connection(host=localhost,port=6379,db=0)>, disable_decoding = False, timeout = None

    async def read_response(
        self,
        disable_decoding: bool = False,
        timeout: Optional[float] = None,
        *,
        disconnect_on_error: bool = True,
        push_request: Optional[bool] = False,
    ):
        """Read the response from a previously sent command"""
        read_timeout = timeout if timeout is not None else self.socket_timeout
        host_error = self._host_error()
        try:
            if (
                read_timeout is not None
                and self.protocol in ["3", 3]
                and not HIREDIS_AVAILABLE
            ):
                async with async_timeout(read_timeout):
                    response = await self._parser.read_response(
                        disable_decoding=disable_decoding, push_request=push_request
                    )
            elif read_timeout is not None:
                async with async_timeout(read_timeout):
                    response = await self._parser.read_response(
                        disable_decoding=disable_decoding
                    )
            elif self.protocol in ["3", 3] and not HIREDIS_AVAILABLE:
                response = await self._parser.read_response(
                    disable_decoding=disable_decoding, push_request=push_request
                )
            else:
>               response = await self._parser.read_response(
                    disable_decoding=disable_decoding
                )

venv/lib/python3.10/site-packages/redis/asyncio/connection.py:579:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
venv/lib/python3.10/site-packages/redis/_parsers/resp2.py:82: in read_response
    response = await self._read_response(disable_decoding=disable_decoding)
venv/lib/python3.10/site-packages/redis/_parsers/resp2.py:90: in _read_response
    raw = await self._readline()
venv/lib/python3.10/site-packages/redis/_parsers/base.py:219: in _readline
    data = await self._stream.readline()
/usr/lib/python3.10/asyncio/streams.py:525: in readline
    line = await self.readuntil(sep)
/usr/lib/python3.10/asyncio/streams.py:617: in readuntil
    await self._wait_for_data('readuntil')
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <StreamReader transport=<_SelectorSocketTransport closing fd=14>>, func_name = 'readuntil'

    async def _wait_for_data(self, func_name):
        """Wait until feed_data() or feed_eof() is called.

        If stream was paused, automatically resume it.
        """
        # StreamReader uses a future to link the protocol feed_data() method
        # to a read coroutine. Running two read coroutines at the same time
        # would have an unexpected behaviour. It would not possible to know
        # which coroutine would get the next data.
        if self._waiter is not None:
            raise RuntimeError(
                f'{func_name}() called while another coroutine is '
                f'already waiting for incoming data')

        assert not self._eof, '_wait_for_data after EOF'

        # Waiting for data while paused will make deadlock, so prevent it.
        # This is essential for readexactly(n) for case when n > self._limit.
        if self._paused:
            self._paused = False
            self._transport.resume_reading()

        self._waiter = self._loop.create_future()
        try:
>           await self._waiter
E           RuntimeError: Task <Task pending name='anyio.from_thread.BlockingPortal._call_func' coro=<BlockingPortal._call_func() running at /home/behai/fastapi_learning/venv/lib/python3.10/site-packages/anyio/from_thread.py:217> cb=[TaskGroup._spawn.<locals>.task_done() at /home/behai/fastapi_learning/venv/lib/python3.10/site-packages/anyio/_backends/_asyncio.py:699]> got Future <Future pending> attached to a different loop

/usr/lib/python3.10/asyncio/streams.py:502: RuntimeError

During handling of the above exception, another exception occurred:

test_client = <starlette.testclient.TestClient object at 0x7fd20bd55c00>

    @pytest.mark.auth_integration
    def test_integration_valid_login(test_client):
        """
        Test /auth/token path with a valid credential.
        """

        try:
            login_data = {
                'username': 'behai_nguyen@hotmail.com',
                'password': 'password'
            }
>           login_response = test_client.post(
                '/auth/token',
                data=login_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

tests/integration/test_auth_itgt.py:37:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
venv/lib/python3.10/site-packages/starlette/testclient.py:633: in post
    return super().post(
venv/lib/python3.10/site-packages/httpx/_client.py:1145: in post
    return self.request(
venv/lib/python3.10/site-packages/starlette/testclient.py:516: in request
    return super().request(
venv/lib/python3.10/site-packages/httpx/_client.py:827: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
venv/lib/python3.10/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
venv/lib/python3.10/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
venv/lib/python3.10/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
venv/lib/python3.10/site-packages/httpx/_client.py:1015: in _send_single_request
    response = transport.handle_request(request)
venv/lib/python3.10/site-packages/starlette/testclient.py:398: in handle_request
    raise exc
venv/lib/python3.10/site-packages/starlette/testclient.py:395: in handle_request
    portal.call(self.app, scope, receive, send)
venv/lib/python3.10/site-packages/anyio/from_thread.py:288: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
/usr/lib/python3.10/concurrent/futures/_base.py:458: in result
    return self.__get_result()
/usr/lib/python3.10/concurrent/futures/_base.py:403: in __get_result
    raise self._exception
venv/lib/python3.10/site-packages/anyio/from_thread.py:217: in _call_func
    retval = await retval_or_awaitable
venv/lib/python3.10/site-packages/fastapi/applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
venv/lib/python3.10/site-packages/starlette/applications.py:123: in __call__
    await self.middleware_stack(scope, receive, send)
venv/lib/python3.10/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
venv/lib/python3.10/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
venv/lib/python3.10/site-packages/starsessions/middleware.py:145: in __call__
    await self.app(scope, receive, send_wrapper)
venv/lib/python3.10/site-packages/starsessions/middleware.py:166: in __call__
    await self.app(scope, receive, send)
venv/lib/python3.10/site-packages/starlette/middleware/exceptions.py:65: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
venv/lib/python3.10/site-packages/starlette/_exception_handler.py:64: in wrapped_app
    raise exc
venv/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    await app(scope, receive, sender)
venv/lib/python3.10/site-packages/starlette/routing.py:756: in __call__
    await self.middleware_stack(scope, receive, send)
venv/lib/python3.10/site-packages/starlette/routing.py:776: in app
    await route.handle(scope, receive, send)
venv/lib/python3.10/site-packages/starlette/routing.py:297: in handle
    await self.app(scope, receive, send)
venv/lib/python3.10/site-packages/starlette/routing.py:77: in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
venv/lib/python3.10/site-packages/starlette/_exception_handler.py:64: in wrapped_app
    raise exc
venv/lib/python3.10/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    await app(scope, receive, sender)
venv/lib/python3.10/site-packages/starlette/routing.py:75: in app
    await response(scope, receive, send)
venv/lib/python3.10/site-packages/starlette/responses.py:152: in __call__
    await send(
venv/lib/python3.10/site-packages/starlette/_exception_handler.py:50: in sender
    await send(message)
venv/lib/python3.10/site-packages/starlette/_exception_handler.py:50: in sender
    await send(message)
venv/lib/python3.10/site-packages/starsessions/middleware.py:125: in send_wrapper
    session_id = await handler.save(remaining_time)
venv/lib/python3.10/site-packages/starsessions/session.py:131: in save
    self.session_id = await self.store.write(
venv/lib/python3.10/site-packages/starsessions/stores/redis.py:68: in write
    await self._connection.set(self.prefix(session_id), data, ex=ttl)
venv/lib/python3.10/site-packages/redis/asyncio/client.py:639: in execute_command
    response = await conn.retry.call_with_retry(
venv/lib/python3.10/site-packages/redis/asyncio/retry.py:59: in call_with_retry
    return await do()
venv/lib/python3.10/site-packages/redis/asyncio/client.py:608: in _send_command_parse_response
    return await self.parse_response(conn, command_name, **options)
venv/lib/python3.10/site-packages/redis/asyncio/client.py:664: in parse_response
    response = await connection.read_response()
venv/lib/python3.10/site-packages/redis/asyncio/connection.py:599: in read_response
    await self.disconnect(nowait=True)
venv/lib/python3.10/site-packages/redis/asyncio/connection.py:452: in disconnect
    self._writer.close()  # type: ignore[union-attr]
/usr/lib/python3.10/asyncio/streams.py:338: in close
    return self._transport.close()
/usr/lib/python3.10/asyncio/selector_events.py:698: in close
    self._loop.call_soon(self._call_connection_lost, None)
/usr/lib/python3.10/asyncio/base_events.py:750: in call_soon
    self._check_closed()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <_UnixSelectorEventLoop running=False closed=True debug=False>

    def _check_closed(self):
        if self._closed:
>           raise RuntimeError('Event loop is closed')
E           RuntimeError: Event loop is closed

/usr/lib/python3.10/asyncio/base_events.py:515: RuntimeError

During handling of the above exception, another exception occurred:

test_client = <starlette.testclient.TestClient object at 0x7fd20bd55c00>

    @pytest.mark.auth_integration
    def test_integration_valid_login(test_client):
        """
        Test /auth/token path with a valid credential.
        """

        try:
            login_data = {
                'username': 'behai_nguyen@hotmail.com',
                'password': 'password'
            }
            login_response = test_client.post(
                '/auth/token',
                data=login_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            assert login_response != None
            assert login_response.status_code == HTTPStatus.OK.value

            status = login_response.json()
            assert status['access_token'] == 'behai_nguyen@hotmail.com'
            assert status['token_type'] == 'bearer'

        finally:
            # Logout. Clean up server sessions.
>           logout(login_response, test_client)
E           UnboundLocalError: local variable 'login_response' referenced before assignment

tests/integration/test_auth_itgt.py:52: UnboundLocalError
=============================================== short test summary info ================================================
FAILED tests/integration/test_auth_itgt.py::test_integration_valid_login - UnboundLocalError: local variable 'login_response' referenced before assignment
============================================= 1 failed, 9 passed in 0.66s ==============================================
(venv) behai@hp-pavilion-15:~/fastapi_learning$
```

## Reloading the ``main`` Module on Every Test

Reloading the ``main`` module on every test results in an **ignored exception**: 🐍 But all tests passed.

```
(venv) behai@hp-pavilion-15:~/fastapi_learning$ venv/bin/pytest
================================================= test session starts ==================================================
platform linux -- Python 3.10.7, pytest-8.2.0, pluggy-1.5.0
rootdir: /home/behai/fastapi_learning
configfile: pytest.ini
plugins: anyio-4.3.0
collected 10 items

tests/integration/test_admin_itgt.py ..                                                                          [ 20%]
tests/integration/test_auth_itgt.py ........                                                                     [100%]

=================================================== warnings summary ===================================================
tests/integration/test_auth_itgt.py::test_integration_root_path_get_login_page
  /home/behai/fastapi_learning/venv/lib/python3.10/site-packages/_pytest/unraisableexception.py:80: PytestUnraisableExceptionWarning: Exception ignored in: <function AbstractConnection.__del__ at 0x7f9cab554670>

  Traceback (most recent call last):
    File "/home/behai/fastapi_learning/venv/lib/python3.10/site-packages/redis/asyncio/connection.py", line 244, in __del__
      self._close()
    File "/home/behai/fastapi_learning/venv/lib/python3.10/site-packages/redis/asyncio/connection.py", line 251, in _close
      self._writer.close()
    File "/usr/lib/python3.10/asyncio/streams.py", line 338, in close
      return self._transport.close()
    File "/usr/lib/python3.10/asyncio/selector_events.py", line 698, in close
      self._loop.call_soon(self._call_connection_lost, None)
    File "/usr/lib/python3.10/asyncio/base_events.py", line 750, in call_soon
      self._check_closed()
    File "/usr/lib/python3.10/asyncio/base_events.py", line 515, in _check_closed
      raise RuntimeError('Event loop is closed')
  RuntimeError: Event loop is closed

    warnings.warn(pytest.PytestUnraisableExceptionWarning(msg))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================================ 10 passed, 1 warning in 0.22s =============================================
Exception ignored in: <function AbstractConnection.__del__ at 0x7f9cab554670>
Traceback (most recent call last):
  File "/home/behai/fastapi_learning/venv/lib/python3.10/site-packages/redis/asyncio/connection.py", line 244, in __del__
    self._close()
  File "/home/behai/fastapi_learning/venv/lib/python3.10/site-packages/redis/asyncio/connection.py", line 251, in _close
    self._writer.close()
  File "/usr/lib/python3.10/asyncio/streams.py", line 338, in close
    return self._transport.close()
  File "/usr/lib/python3.10/asyncio/selector_events.py", line 698, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/usr/lib/python3.10/asyncio/base_events.py", line 750, in call_soon
    self._check_closed()
  File "/usr/lib/python3.10/asyncio/base_events.py", line 515, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
(venv) behai@hp-pavilion-15:~/fastapi_learning$
```