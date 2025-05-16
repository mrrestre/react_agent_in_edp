class Util:
    """Collection of utilities for Fact Score generation"""

    @staticmethod
    def remove_json_code_block_markers(text: str) -> str:
        """
        Removes the ```json and ``` markers from a string.

        Args:
            text: The input string potentially containing the markers.

        Returns:
            The string with the markers removed.
        """
        # Remove the starting marker
        if text.startswith("```json\n"):
            text = text[len("```json\n") :]

        # Remove the ending marker
        if text.endswith("\n```"):
            text = text[: -len("\n```")]
        elif text.endswith(
            "```"
        ):  # Handle cases without a newline before the ending ```
            text = text[: -len("```")]

        return text
