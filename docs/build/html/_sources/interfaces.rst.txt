Interfaces
==========

.. currentmodule:: _sassy.i_sassy

.. py:class::  MessagesInterfaces

    Message abstract class (Interface).

.. py:method:: MessagesInterfaces.msg(name: str, extra: _t.Optional[str] = None) -> Message

    Read a message.

    :param name: The message name.
    :type name: str
    :param extra: Extra information.
    :type extra: Optional[str]
    :return: A ``Message`` :abbr:`DTO (Data Transfer Object)`.
    :rtype: ``Message``