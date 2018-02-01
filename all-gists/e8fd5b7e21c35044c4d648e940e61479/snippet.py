def createStore(reducer, state, enhancer):
    """
        Store instance constructor

        Usage:

        .. code-block: python

            from store import createStore

            initialState = {
                data: 1
            }

            def myReducer(state, action):
                # Access properies with dot notation!
                if action.type == 'INCREMENT':
                    return state.data + action.data

            # Same interface as Redux
            store = createStore(myReducer, initalState)
            print(str(store.getState()))  # { 'data': 1 }

            store.dispatch({'type': 'INCREMENT', 'data': 1})
            print(str(store.getState()))  # { 'data': 2 }
     """
    return Store(reducer, state, enhancer)


class Store:
    def __init__(self, reducer, preLoadedState, enhancer):
        self._reducer = reducer
        self._state = preLoadedState
        self._enhancer = enhancer  # TODO

    def getState(self):
        return self._state

    def dispatch(self, action):
        self._state = self._reducer(*_wrapAction(self._state, action))


def _wrapAction(state, action):
    class objectView:
        def __init__(self, inner):
            self.__dict__ = inner

    actionView = objectView(action)
    stateView = objectView(state) if isinstance(state, dict) else state
    return stateView, actionView
