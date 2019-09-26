SELECT s.[Name]
     ,q.[JobQueueID]
     ,q.[Placed]
      ,DATEDIFF(minute, q.[Placed], GETUTCDATE()) AS WaitInMinutes
      ,DATEDIFF(minute, q.[Placed], GETUTCDATE())/60.00 AS WaitInHours
     ,q.[SubscriptionID]
     ,q.[ProcessId]
 FROM [IASDB].[dbo].[JobQueue] AS q
 INNER JOIN
 [IASDB].[dbo].[BO_Subscription] AS s
 ON q.[SubscriptionID] = s.[SubscriptionID]
 ORDER BY WaitInHours DESC
