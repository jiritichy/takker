import os
import time
import random

from api.info import get_stranger_info

from service.db.utils.point import add_random_points
from .data_source import get_acg_image, get_stick, get_greet, get_msg
from configs.path_config import TEMPLATE_PATH, IMAGE_PATH
from utils.browser import get_browser


async def get_card(user_id: int):
    stick = await get_stick(user_id)
    acg_url = await get_acg_image()
    user_name = (await get_stranger_info(user_id))["nickname"]
    day_time = time.strftime(r"%m/%d", time.localtime())
    date = time.strftime(r"%Y-%m-%d", time.localtime())
    random.seed()
    cardname = random.choice(["card1", "card2"])
    with open(f"{TEMPLATE_PATH}check_in/{cardname}.html", "r", encoding="utf-8") as f:
        template = str(f.read())

    filename = f"temp-card-{user_id}"

    if os.path.isfile(f"{TEMPLATE_PATH}/check_in/temp/{filename}.html"):
        modifiedTime = time.localtime(
            os.stat(f"{TEMPLATE_PATH}/check_in/temp/{filename}.html").st_mtime
        )
        mtime = time.strftime(r"%Y%m%d", modifiedTime)
        ntime = time.strftime(r"%Y%m%d", time.localtime(time.time()))
        if mtime != ntime:
            points = await add_random_points(user_id, 20)
            template = template.replace("[points]", str(points))
        else:
            template = template.replace("[points]", "0(已经签到过啦)")
    else:
        points = await add_random_points(user_id, 20)
        template = template.replace("[points]", str(points))

    template = template.replace("static/", "../static/")
    template = template.replace("[acg_url]", acg_url)
    template = template.replace("[greet]", await get_greet())
    template = template.replace(
        "[msg_of_the_day]", (await get_msg(user_id))["SENTENCE"]
    )
    template = template.replace(
        "[avatar_url]", f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    )
    template = template.replace("[day_time]", day_time)
    template = template.replace("[date]", date)
    template = template.replace("[user_name]", user_name)
    template = template.replace("[luck-status]", stick["FORTUNE_SUMMARY"])
    template = template.replace("[star]", stick["LUCKY_STAR"])
    template = template.replace("[comment]", stick["SIGN_TEXT"])
    template = template.replace("[resolve]", stick["UN_SIGN_TEXT"])

    with open(
        f"{TEMPLATE_PATH}check_in/temp/{filename}.html", "w", encoding="utf-8"
    ) as f:
        f.write(template)

    return await generate_pic(filename)


async def generate_pic(filename: str):
    browser = await get_browser()
    page = await browser.new_page()
    await page.goto(f"file://{TEMPLATE_PATH}check_in/temp/{filename}.html")
    card = await page.query_selector(".card")
    assert card is not None
    img = await card.screenshot(type="png")
    await page.close()
    return img
