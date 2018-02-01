def compare_on_dataset(data, target_variable=None, lr=0.001, patience=150):
    
    from IPython.display import display
    
    df = (
        pd.read_csv(data)

        # Rename columns to lowercase and underscores
        .pipe(lambda d: d.rename(columns={
            k: v for k, v in zip(
                d.columns, 
                [c.lower().replace(' ', '_') for c in d.columns]
            )
        }))
        # Switch categorical classes to integers
        .assign(**{target_variable: lambda r: r[target_variable].astype('category').cat.codes})
        .pipe(lambda d: pd.get_dummies(d))
    )

    y = df[target_variable].values
    X = (
        # Drop target variable
        df.drop(target_variable, axis=1)
        # Min-max-scaling (only needed for the DL model)
        .pipe(lambda d: (d-d.min())/d.max()).fillna(0)
        .as_matrix()
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=seed
    )

    m = Sequential()
    m.add(Dense(128, activation='relu', input_shape=(X.shape[1],)))
    m.add(Dropout(0.5))
    m.add(Dense(128, activation='relu'))
    m.add(Dropout(0.5))
    m.add(Dense(128, activation='relu'))
    m.add(Dropout(0.5))
    m.add(Dense(len(np.unique(y)), activation='softmax'))

    m.compile(
        optimizer=optimizers.Adam(lr=lr),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    m.fit(
        # Feature matrix
        X_train, 
        # Target class one-hot-encoded
        pd.get_dummies(pd.DataFrame(y_train), columns=[0]).as_matrix(),
        # Iterations to be run if not stopped by EarlyStopping
        epochs=200, 
        callbacks=[
            EarlyStopping(monitor='val_loss', patience=patience),
            ModelCheckpoint(
                'best.model', 
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            )
        ],
        verbose=2,
        validation_split=0.1,
        batch_size=256, 
    )

    # Keep track of what class corresponds to what index
    mapping = (
        pd.get_dummies(pd.DataFrame(y_train), columns=[0], prefix='', prefix_sep='')
        .columns.astype(int).values
    )
    
    # Load the best model
    m.load_weights("best.model")
    y_test_preds = [mapping[pred] for pred in m.predict(X_test).argmax(axis=1)]

    print 'Three layer deep neural net'
    display(pd.crosstab(
        pd.Series(y_test, name='Actual'),
        pd.Series(y_test_preds, name='Predicted'),
        margins=True
    ))

    print 'Accuracy: {0:.3f}'.format(accuracy_score(y_test, y_test_preds)) 
    boostrap_stats_samples = [
    np.random.choice((y_test == y_test_preds), size=int(len(y_test)*.5)).mean() 
        for _ in range(10000)
    ]
    print 'Boostrapped accuracy 95 % interval', np.percentile(boostrap_stats_samples, 5), np.percentile(boostrap_stats_samples, 95)

    params_fixed = {
        'objective': 'binary:logistic',
        'silent': 1,
        'seed': seed,
    }
    space = {
        'max_depth': (1, 5),
        'learning_rate': (10**-4, 10**-1),
        'n_estimators': (10, 200),
        'min_child_weight': (1, 20),
        'subsample': (0, 1),
        'colsample_bytree': (0.3, 1)
    }
    reg = XGBClassifier(**params_fixed)

    def objective(params):
        """ Wrap a cross validated inverted `accuracy` as objective func """
        reg.set_params(**{k: p for k, p in zip(space.keys(), params)})
        return 1-np.mean(cross_val_score(
            reg, X_train, y_train, cv=5, n_jobs=-1,
            scoring='accuracy')
        )
    
    res_gp = gp_minimize(objective, space.values(), n_calls=50, random_state=seed)
    best_hyper_params = {k: v for k, v in zip(space.keys(), res_gp.x)}

    params = best_hyper_params.copy()
    params.update(params_fixed)

    clf = XGBClassifier(**params)
    clf.fit(X_train, y_train)
    y_test_preds = clf.predict(X_test)
    
    print ''
    print 'Xgboost'
    display(pd.crosstab(
        pd.Series(y_test, name='Actual'),
        pd.Series(y_test_preds, name='Predicted'),
        margins=True
    ))
    print 'Accuracy: {0:.3f}'.format(accuracy_score(y_test, y_test_preds))
    boostrap_stats_samples = [
    np.random.choice((y_test == y_test_preds), size=int(len(y_test)*.5)).mean() 
        for _ in range(10000)
    ]
    print 'Boostrapped accuracy 95 % interval', np.percentile(boostrap_stats_samples, 5), '-', np.percentile(boostrap_stats_samples, 95)