import asyncio
from twitch_bot.data.logger import logger


class sceneItemTransform:
    def __init__(
        self,
        alignment=5,
        bounds_alignment=0,
        bounds_height=1.0,
        bounds_type="OBS_BOUNDS_NONE",
        bounds_width=1.0,
        crop_bottom=0,
        crop_left=0,
        crop_right=0,
        crop_top=0,
        height=1.0,
        position_x=0.0,
        position_y=0.0,
        rotation=0.0,
        scale_x=1.0,
        scale_y=1.0,
        source_height=1.0,
        source_width=1.0,
        width=1.0,
    ):
        self.alignment = alignment
        self.bounds_alignment = bounds_alignment
        self.bounds_height = bounds_height
        self.bounds_type = bounds_type
        self.bounds_width = bounds_width
        self.crop_bottom = crop_bottom
        self.crop_right = crop_right
        self.crop_top = crop_top
        self.position_x = position_x
        self.position_y = position_y
        self.rotation = rotation
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.source_height = source_height
        self.source_width = source_width
        self.width = width

    async def get(self):
        scene_item_transform = {
            "alignment": self.alignment,
            "boundsAlignment": self.bounds_alignment,
            "boundsHeight": self.bounds_height,
            "boundsType": self.bounds_type,
            "boundsWidth": self.bounds_width,
            "cropBottom": self.crop_bottom,
            "cropLeft": self.crop_left,
            "cropRight": self.crop_right,
            "cropTop": self.crop_top,
            "height": self.height,
            "positionX": self.position_x,
            "positionY": self.position_y,
            "rotation": self.rotation,
            "scaleX": self.scale_x,
            "scaleY": self.scale_y,
            "sourceHeight": self.source_height,
            "sourceWidth": self.source_width,
            "width": self.width,
        }
        return scene_item_transform


async def set_scene_item_transform(
    self,
    scene_name: str = None,
    item_id: int = None,
    x: int = None,
    y: int = None,
    x_start: int = None,
    y_start: int = None,
    x_end: int = None,
    y_end: int = None,
    duration: float = None,
    delay: float = None,
):
    if not scene_name:
        logger.error("[obs] ! scene_name was not set.")
    elif not item_id:
        logger.error("[obs] ! item_id was not set.")
    elif not ((x and y) or (duration and (x and y_start and y_end) or (y and x_start and x_end))):
        logger.error("[obs] ! Needs x and y or _start and _end for x and y")
    else:
        request_type = "SetSceneItemTransform"
        request_data = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
        }

        if delay:
            await asyncio.sleep(delay)

        if x and y:
            scene_item_transform = self.sceneItemTransform(position_x=x, position_y=y)
            request_data.update({"sceneItemTransform": await scene_item_transform.get()})
            await self.send_request(request_type, request_data)
        else:

            if not x_start:
                x_start = x
            if not y_start:
                y_start = y

            if not x_end:
                x_end = x_start
            if not y_end:
                y_end = y_start

            x_diff = x_end - x_start
            y_diff = y_end - y_start

            x_step = int(abs(x_diff) * 0.1)
            y_step = int(abs(y_diff) * 0.1)

            if x_diff < 0:
                x_step = x_step * -1

            if y_diff < 0:
                y_step = y_step * -1

            if x_diff == 0:
                x_range = [x_start]
            else:
                x_range = [*range(x_start, x_end, x_step)]

            if y_diff == 0:
                y_range = [y_start]
            else:
                y_range = [*range(y_start, y_end, y_step)]

            x_count = len(x_range)
            y_count = len(y_range)
            max_count = max([abs(x_count), abs(y_count)])
            wait_time = duration / max_count

            if x_count > y_count:
                y_padding = int(y_end / (x_count / y_count))
                _y_range = []
                for y in y_range:
                    _y_range.extend([y] * y_padding)
                y_range = _y_range
            elif y_count > x_count:
                x_padding = int(x_end / (y_count / x_count))
                _x_range = []
                for x in x_range:
                    _x_range.extend([x] * x_padding)
                x_range = _x_range

            xy_range = list(zip(x_range, y_range))
            for x, y in xy_range:
                scene_item_transform = self.sceneItemTransform(position_x=x, position_y=y)
                request_data.update({"sceneItemTransform": await scene_item_transform.get()})
                await self.send_request(request_type, request_data)
                await asyncio.sleep(wait_time)
