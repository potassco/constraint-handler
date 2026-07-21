from __future__ import annotations

from flat_ch.core.serialization import BaseSerializer


class FCHSerializer(BaseSerializer):
    """FCH dialect serializer: Floats represented directly as String literals ("3.5")."""
