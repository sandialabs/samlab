# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import os
import time

from behave import *

import samlab.dashboard

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@given(u'a running dashboard server')
def step_impl(context):
    def cleanup(dashboard):
        dashboard.stop()

    context.dashboard = samlab.dashboard.Server(config=False, coverage=True, quiet=True)
    context.add_cleanup(cleanup, context.dashboard)
    context.dashboard.ready(timeout=10)


@given(u'a connected browser')
def step_impl(context):
    def cleanup(browser):
        browser.close()

    from selenium.webdriver import Firefox
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.support.ui import WebDriverWait as Wait
    from selenium.webdriver.support.expected_conditions import presence_of_element_located as element_located

    options = Options()
    options.headless = True

    context.browser = Firefox(options=options)
    context.browser.get(context.dashboard.uri)
    context.browser_wait = Wait(context.browser, timeout=10)
    context.browser_wait.until(element_located((By.ID, "samlab-notify-container")))
    time.sleep(1.0) # Give the page a chance to settle-down.

