"""
Domains for sassy.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import dataclasses as _dt
import typing as _t
import enum as _enum


@_dt.dataclass
class Result:
    """Result DTO."""

    _ok: _t.Optional[str] = None
    _err: _t.Optional[str] = None

    def __str__(self) -> str:
        """Rewrite Result as a string."""
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

    class SeverityLevel(_enum.Enum):
        """Severity levels."""

        DEBUG = 10
        INFO = 20
        WARNING = 30
        ERROR = 40
        CRITICAL = 50

    def __repr__(self) -> str:
        """Message machine-readable."""
        return f"{self.__class__.__name__}" \
               f"(code: {self.code}, severity: {self.severity}, " \
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

    def level(self):
        """Get the severity level."""
        if self.severity in self.SeverityLevel.__members__:
            return self.SeverityLevel[self.severity].value
        return self.SeverityLevel['INFO'].value


@_dt.dataclass
class File:
    """File DTO."""

    name: str
    content: _t.Optional[str] = ''

    def replace_content(
            self,
            payload: _t.Dict[str, _t.Any]
    ) -> str:
        """
        Rename the content file.

        Args:
            payload: A key, value that represent what needs to be replaced
                    and by which value.
                    key: The key that needs to be replaced
                    value: The value that will be apply

        Returns:
            The content with string replaced.
        """
        if self.content:
            for k, v in payload.items():
                self.content = self.content.replace(k, v)

        return self.content

    def replace_file_name(
            self,
            payload: _t.Dict[str, _t.Any]
    ) -> str:
        """
        Replace the file name.

        Args:
            payload: A key, value that represent what needs to be replaced
                    and by which value.
                    key: The key that needs to be replaced
                    value: The value that will be apply

        Returns:
            The file name with string replaced.
        """
        if self.name:
            for k, v in payload.items():
                self.name = self.name.replace(k, v)

        return self.name


@_dt.dataclass
class Struct:
    """Struct DTO."""

    name: str
    dirs: _t.List[_t.Any]
    files: _t.List[File]
