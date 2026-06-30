import json
import logging
import urllib.request
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, AudioItemMetadata, Stream, StopDirective
)
from ask_sdk_model.interfaces.display.image import Image as DisplayImage
from ask_sdk_model.interfaces.display.image_instance import ImageInstance

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

STREAM_URL = "https://streaming.live365.com/a77923"
STREAM_TOKEN = "freaksonly-fm-live"
STATION_NAME = "Freaks Only F M"
METADATA_URL = "https://api.live365.com/station/a77923"
ICON_URL = "https://freaksonlyfm-alexa-assets.s3.amazonaws.com/icon512.png"

sb = SkillBuilder()


def _build_metadata():
    art = DisplayImage(sources=[ImageInstance(url=ICON_URL)])
    return AudioItemMetadata(
        title=STATION_NAME,
        subtitle="Powered by Live365",
        art=art,
        background_image=art,
    )


def _play_directive():
    return PlayDirective(
        play_behavior=PlayBehavior.REPLACE_ALL,
        audio_item=AudioItem(
            stream=Stream(
                token=STREAM_TOKEN,
                url=STREAM_URL,
                offset_in_milliseconds=0,
            ),
            metadata=_build_metadata(),
        ),
    )


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        return (
            handler_input.response_builder
            .speak(f"Starting {STATION_NAME}.")
            .add_directive(_play_directive())
            .response
        )


class PlayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            is_intent_name("PlayAudioIntent")(handler_input)
            or is_intent_name("AMAZON.ResumeIntent")(handler_input)
        )

    def handle(self, handler_input):
        return (
            handler_input.response_builder
            .add_directive(_play_directive())
            .response
        )


class StopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            is_intent_name("AMAZON.StopIntent")(handler_input)
            or is_intent_name("AMAZON.CancelIntent")(handler_input)
            or is_intent_name("AMAZON.PauseIntent")(handler_input)
        )

    def handle(self, handler_input):
        return (
            handler_input.response_builder
            .add_directive(StopDirective())
            .response
        )


class NowPlayingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("NowPlayingIntent")(handler_input)

    def handle(self, handler_input):
        try:
            with urllib.request.urlopen(METADATA_URL, timeout=3) as resp:
                data = json.loads(resp.read())
            track = data.get("current-track", {})
            title = track.get("title", "").strip()
            artist = track.get("artist", "").strip()
            if title and artist:
                speech = f"Now playing: {title}, by {artist}."
            elif title:
                speech = f"Now playing: {title}."
            else:
                speech = "I couldn't get the current track info right now."
        except Exception:
            speech = "I couldn't reach the station info right now."
        return handler_input.response_builder.speak(speech).response


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        return (
            handler_input.response_builder
            .speak(
                f"{STATION_NAME} is live 24/7 internet radio from Los Angeles. "
                "Say play to start listening, stop to turn it off, "
                "or ask what's playing to find out the current track."
            )
            .response
        )


class UnsupportedIntentHandler(AbstractRequestHandler):
    """Handles intents that don't apply to a single live-radio stream."""

    def can_handle(self, handler_input):
        return any(is_intent_name(n)(handler_input) for n in [
            "AMAZON.NextIntent",
            "AMAZON.PreviousIntent",
            "AMAZON.StartOverIntent",
            "AMAZON.LoopOnIntent",
            "AMAZON.LoopOffIntent",
            "AMAZON.ShuffleOnIntent",
            "AMAZON.ShuffleOffIntent",
        ])

    def handle(self, handler_input):
        return (
            handler_input.response_builder
            .speak("That feature isn't available for live radio.")
            .response
        )


class PlaybackControllerHandler(AbstractRequestHandler):
    """Handles hardware button presses on Echo devices."""

    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.object_type.startswith(
            "PlaybackController."
        )

    def handle(self, handler_input):
        request_type = handler_input.request_envelope.request.object_type
        if request_type == "PlaybackController.PlayCommandIssued":
            return (
                handler_input.response_builder
                .add_directive(_play_directive())
                .response
            )
        return (
            handler_input.response_builder
            .add_directive(StopDirective())
            .response
        )


class AudioPlayerEventHandler(AbstractRequestHandler):
    """Acknowledge AudioPlayer lifecycle events (required by Alexa)."""

    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.object_type.startswith(
            "AudioPlayer."
        )

    def handle(self, handler_input):
        if handler_input.request_envelope.request.object_type == "AudioPlayer.PlaybackFailed":
            return (
                handler_input.response_builder
                .add_directive(_play_directive())
                .response
            )
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PlayIntentHandler())
sb.add_request_handler(NowPlayingIntentHandler())
sb.add_request_handler(StopIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(UnsupportedIntentHandler())
sb.add_request_handler(PlaybackControllerHandler())
sb.add_request_handler(AudioPlayerEventHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
