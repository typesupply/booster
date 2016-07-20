import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController

class Test(BaseWindowController):

    def __init__(self):
        self.extensionManager = ExtensionManager(
            owner="My Extension",
            userDefaults=dict(
                foo=1,
                bar=2
            ),
            menu = dict(
                title="My Extension",
                items=[
                    dict(
                        title="My Item"
                    ),
                    dict(
                        title="My Item with Key Command",
                        binding=("5", ["command", "option"])
                    )
                ]
            )
        )
        self.w = vanilla.Window((500, 500))
        self.w.open()
        self.setUpBaseWindowBehavior()

    def windowCloseCallback(self, sender):
        super(Test, self).windowCloseCallback(sender)
        self.extensionManager.teardown()

if __name__ == "__main__":
    if environment.inRoboFont:
        Test()
    else:
        from vanilla.test.testTools import executeVanillaTest
        executeVanillaTest(Test)