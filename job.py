"""The one normalized shape every source produces."""

import hashlib
from dataclasses import dataclass, field


@dataclass
class Job:
    company: str
    title: str
    url: str
    location: str = ""
    source: str = ""          # "github:Simplify", "greenhouse", ...
    date_posted: str = ""     # free-form; whatever the source gives

    # Fields used only for filtering, not display. Populated when a source has
    # richer text than the title alone (e.g. a job description).
    extra_text: str = field(default="", repr=False)

    def uid(self) -> str:
        """
        Stable identity used for de-duplication across runs.

        Prefer the apply URL (most stable). Fall back to company+title so a
        posting without a clean URL still de-dupes sanely.
        """
        basis = self.url.strip().lower() or f"{self.company}|{self.title}".lower()
        return hashlib.sha1(basis.encode("utf-8")).hexdigest()

    def haystack(self) -> str:
        """All the text we run keyword filters against, lowercased."""
        return " ".join(
            [self.company, self.title, self.location, self.extra_text]
        ).lower()
