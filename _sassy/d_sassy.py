"""
Domains for sassy.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import dataclasses as _dt
import typing as _t


@_dt.dataclass
class Result:
    """Result DTO."""

    _ok: _t.Optional[str] = None
    _err: _t.Optional[str] = None

    def __str__(self) -> str:
        """"""
        if self.ok:
            return f'{self.ok}'
        else:
            return f'{self.err}'

    @property
    def ok(self) -> _t.Any:
        """
        Get ok.

        Returns:
            The ok result.
        """
        return self._ok

    @ok.setter
    def ok(self, val: _t.Any):
        """
        Set ok.

        Args:
            val: Any value
        """
        if val:
            self._ok = val
            self._err = None

    @property
    def err(self) -> _t.Any:
        """
        Get error.

        Returns:
            Any error
        """
        return self._err

    @err.setter
    def err(self, val: _t.Any):
        """
        Set error.

        Args:
            val: Any value
        """
        if val:
            self._err = val
            self._ok = None


@_dt.dataclass
class Message:
    """Message DTO."""

    code: int
    severity: str
    _text = None
    extra: _t.Optional[str] = None

    def __repr__(self) -> str:
        """Message machine-readable."""
        return f"Message(code: {self.code}, severity: {self.severity}, " \
               f"text: {self.text})"

    def __str__(self) -> str:
        """Message human-readable."""
        return f"({self.code},{self.severity},{self.text})"

    def as_dict(self) -> _t.Dict[str, _t.Any]:
        """Convert Message as a dict."""
        return {
            "code": self.code,
            "severity": self.severity,
            "text": self.text
        }

    @property
    def text(self) -> str:
        """Get text value."""
        return self._text

    @text.setter
    def text(self, text: str):
        """Set text value."""
        self._text = text.replace("'{}' ", "")

        if self.extra:
            self._text = text.format(self.extra)
