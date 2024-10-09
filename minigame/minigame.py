from abc import ABC, abstractmethod

class Minigame(ABC):
    @abstractmethod
    def commands(self) -> list[str]:
        """
        ミニゲームを起動するためのコマンドのリスト (アルファベットは小文字で指定)
        """
        pass

    @abstractmethod
    def help(self) -> str:
        """
        ミニゲームチャンネルでヘルプコマンドが呼び出されたときに表示する、簡単な説明文
        """
        pass

    @abstractmethod
    def help_detail(self) -> str:
        """
        コマンド名を指定してヘルプコマンドが呼び出されたときに表示する、詳細な説明文
        help() で指定した説明文の後に続けて表示される
        """
        pass

    @abstractmethod
    async def play(self, args: list[str]) -> None:
        """
        ゲームを始める
        
        :param list[str] args: ゲーム起動時に与えられた引数
        """
        pass